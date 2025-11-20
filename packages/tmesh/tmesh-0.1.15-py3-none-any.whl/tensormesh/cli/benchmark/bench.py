import sys
import os
import requests
import signal
from dataclasses import dataclass
from openai import OpenAI, AsyncOpenAI, APIConnectionError, RateLimitError, APIError, BadRequestError, AuthenticationError, NotFoundError
from typing import Union, Any
import asyncio
import importlib.resources
import json
import random
import time
from urllib.parse import urlparse, urlunparse

@dataclass
class RequestStats: 
    start_time: float
    first_token_time: float
    end_time: float
    input_length: int
    output_length: int

@dataclass
class PrefillPairs: 
    input_length: int
    prefill_time: float

@dataclass
class DecodePairs: 
    output_length: int
    decode_time: float

class ObservabilityPanel: 
    def __init__(self, workload_config: "WorkloadConfig"): 
        print(
            f"\n\n\nNOTE: tmesh-cli benchmark will run forever until you interrupt the process.\n\n\n"
            f"Workload Specifications:\n"
            f"Model: {workload_config.model_name}\n"
            f"Number of Contexts: {workload_config.num_contexts}\n"
            f"Number of Questions per Context: {workload_config.questions_per_context}\n"
            f"Max Inflight Requests (Load-Balancing): {workload_config.max_inflight_requests}\n"
            f"Input Length: {workload_config.input_length}\n"
            f"Output Length: {workload_config.output_length}\n"
        )
        self.num_requests = 0
        # cleared after every non-empty interval
        self.interval_requests = 0
        self.interval_prefill_stats: list[PrefillPairs] = []
        self.interval_decode_stats: list[DecodePairs] = []

        self.running_ttft = 0
        self.running_itl = 0
        self.running_prefill_throughput = 0
        self.running_decode_throughput = 0
        self.start_time = time.time()

        # every 5 seconds, we will update the current values
        self.log_update_interval = 5
    
    async def start(self): 
        asyncio.create_task(self.stat_logger())

    def on_request_finished(self, request_stats: RequestStats):
        self.interval_requests += 1
        self.interval_prefill_stats.append(PrefillPairs(request_stats.input_length, request_stats.first_token_time - request_stats.start_time))
        self.interval_decode_stats.append(DecodePairs(request_stats.output_length, request_stats.end_time - request_stats.first_token_time))
    
    # an async daemon
    async def stat_logger(self): 
        while True: 
            now = time.time()
            elapsed_time = now - self.start_time
            total_requests = self.num_requests + self.interval_requests
            # avoid division by zero if we didn't finish any requests in this interval
            if not self.interval_prefill_stats or not self.interval_decode_stats:
                await asyncio.sleep(self.log_update_interval)
                continue
            interval_ttft = sum(prefill_pair.prefill_time for prefill_pair in self.interval_prefill_stats) / len(self.interval_prefill_stats)
            # + 1 for EOS token
            interval_itl = sum(decode_pair.decode_time / (decode_pair.output_length + 1) for decode_pair in self.interval_decode_stats) / len(self.interval_decode_stats)
            interval_prefill_throughput = sum(prefill_pair.input_length / prefill_pair.prefill_time for prefill_pair in self.interval_prefill_stats) / len(self.interval_prefill_stats)
            interval_decode_throughput = sum(decode_pair.output_length / decode_pair.decode_time for decode_pair in self.interval_decode_stats) / len(self.interval_decode_stats)
            old_weight, new_weight = self.num_requests / total_requests, self.interval_requests / total_requests
            self.running_ttft = old_weight * self.running_ttft + new_weight * interval_ttft
            self.running_itl = old_weight * self.running_itl + new_weight * interval_itl
            self.running_prefill_throughput = old_weight * self.running_prefill_throughput + new_weight * interval_prefill_throughput
            self.running_decode_throughput = old_weight * self.running_decode_throughput + new_weight * interval_decode_throughput

            self.num_requests = total_requests
            qps = self.num_requests / elapsed_time
            self.interval_prefill_stats = []
            self.interval_decode_stats = []
            print(
                f"Elapsed Time: {elapsed_time}\n"
                f"Total Number of Requests Processed: {self.num_requests}\n"
                f"QPS: {qps}\n"
                f"Global Average TTFT: {self.running_ttft}\n"
                f"Global Average ITL: {self.running_itl}\n"
                f"Global Average Prefill Throughput: {self.running_prefill_throughput}\n"
                f"Global Average Decode Throughput: {self.running_decode_throughput}\n"
                f"Requests Processed in Last {self.log_update_interval} second Interval: {self.interval_requests}\n"
                f"Interval Average TTFT: {interval_ttft}\n"
                f"Interval Average ITL: {interval_itl}\n"
                f"Interval Average Prefill Throughput: {interval_prefill_throughput}\n"
                f"Interval Average Decode Throughput: {interval_decode_throughput}\n"
            )
            self.interval_requests = 0
            await asyncio.sleep(self.log_update_interval)
            


@dataclass
class WorkloadConfig: 
    num_contexts: int
    questions_per_context: int
    model_name: str
    max_inflight_requests: int
    # hardcoded for now
    input_length: int = 10000
    output_length: int = 100

    @staticmethod
    def _find_model(endpoint: str, api_key: str) -> str:

        # helper function that queries for available model differently depending on the endpoint provider
        def _query_available_models() -> list[Union[dict, Any]]:
            if "together" in endpoint.lower(): 
                print("TogetherAI endpoint detected")
                resp = requests.get(
                    f"{endpoint}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                resp.raise_for_status()
                data = resp.json()
                # together will return all of their models (the model is not coupled to your API key or endpoint)
                # Only keep ids with >= 3 slash-separated components
                # <user>/<namespace>/<model_id>
                data = [
                    model for model in data
                    if len((model["id"] if isinstance(model, dict) else model.id).split("/")) >= 3
                ]
            elif "fireworks" in endpoint.lower(): 
                print("FireworksAI endpoint detected")
                # first find the model
                resp = requests.get(
                    f"{endpoint.replace("inference/", "")}/accounts",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                resp.raise_for_status()
                account_data = resp.json()
                account_id = account_data["accounts"][0]["name"].replace("accounts/", "")

                # look for deployments under the account id
                resp = requests.get(
                    f"{endpoint.replace("inference/", "")}/accounts/{account_id}/deployments",
                    headers={"Authorization": f"Bearer {api_key}"}
                )

                resp.raise_for_status()
                deployment_data = resp.json()
                # extract two things
                # the baseModel
                # the deployment name

                first_deployment = deployment_data["deployments"][0]

                base_model = first_deployment["baseModel"]
                deployment_name = first_deployment["name"]
                data = [{"id": f"{base_model}#{deployment_name}"}]
            else: 
                print("Using default OpenAI SDK / API")
                client = OpenAI(base_url=endpoint, api_key=api_key)
                models = client.models.list()
                data = models.data

            if not data:
                raise RuntimeError("No models returned from endpoint.")
            return data
        
        data = _query_available_models()

        # load in the hardcoded model configs from Tensormesh SaaS
        with importlib.resources.files("tensormesh.cli.benchmark").joinpath("model_configs.json").open("r") as f:
            model_configs = json.load(f)

        model_names = {m["model_name"] for m in model_configs if m.get("model_name")}
        model_short_searches = [m["search"] for m in model_configs if m.get("search")]

        model_id = None

        for model in data:
            mid = model["id"] if isinstance(model, dict) else model.id
            if mid in model_names:
                model_id = mid
                break
            for s in model_short_searches:
                if s.lower() in mid.lower():
                    model_id = mid
                    break

        if not model_id:
            raise RuntimeError(
                "No model found in model_configs.json. "
                "Use one of:\n" + "\n".join(model_names)
            )

        print(f"found model: {model_id}")
        return model_id

    @staticmethod
    def calculate_workload(model_config: dict, model_id: str) -> "WorkloadConfig": 
        tp = int(model_config["tensorParallelSize"])
        cpu_size = int(model_config["cpuOffloadingBufferSize"])
        disk_size = int(model_config["diskOffloadingBufferSize"])
        remote_size = int(model_config["remoteOffloadingBufferSize"])
        bytes_per_tok = int(model_config["bytes_per_tok"])
        offload_size = max(cpu_size * tp, disk_size * tp, remote_size)
        print(f"offload_size: {offload_size}")
        # 80% of the buffer we have (accounting for fragmentation etc.)
        conservative_ratio = 0.8
        num_contexts = int((conservative_ratio * offload_size) // (bytes_per_tok * (WorkloadConfig.input_length + WorkloadConfig.output_length + 8) / 1024 ** 3))
        questions_per_context = num_contexts
        # have 1/3 of the contexts be inflight at any time
        max_inflight_requests = num_contexts // 3
        return WorkloadConfig(
            num_contexts=num_contexts,
            questions_per_context=questions_per_context,
            model_name=model_id,
            max_inflight_requests=max_inflight_requests,
            input_length=WorkloadConfig.input_length,
            output_length=WorkloadConfig.output_length)

    @staticmethod
    def from_endpoint(endpoint: str, api_key: str) -> "WorkloadConfig": 
        # assumptions: 
        # all of the hardcoded specs are inside of model_configs.json
        # this will automatically match a model name to: 
        # TP, bytes_per_tok, cpu size, disk size, remote size
        # we will create a workload that maximally stresses a buffer of size
        # max(cpu size * TP, disk size * TP, remote size)
        model = WorkloadConfig._find_model(endpoint, api_key)
        with importlib.resources.files("tensormesh.cli.benchmark").joinpath("model_configs.json").open("r") as f:
            model_configs = json.load(f)
            for model_config in model_configs:
                if model_config["model_name"] == model or model_config["search"] in model:
                    return WorkloadConfig.calculate_workload(model_config, model)

class WorkloadGenerator: 
    @staticmethod
    def generate_context_pool(num_contexts: int, context_length: int) -> list[str]: 
        return [f"{i}" + "hi" * context_length for i in range(num_contexts)]
    
    @staticmethod
    def generate_question_pool(num_questions: int) -> list[str]: 
        return [f"{i}" + "tell me a long story" for i in range(num_questions)]
    
    @staticmethod
    def has_content(chunk): 
        return bool(chunk.choices) and (chunk.choices[0].text is not None)
    
    @staticmethod
    def extract_content(chunk): 
        return chunk.choices[0].text or ""

    def __init__(self, workload_config: "WorkloadConfig", endpoint: str, api_key: str): 
        self.observability_panel = ObservabilityPanel(workload_config)
        self.workload_config = workload_config
        print(f"Open AI client setup with endpoint: {endpoint} and api_key: {api_key}")
        self.client = AsyncOpenAI(
            base_url=endpoint, 
            api_key=api_key
        )
        self.context_pool = WorkloadGenerator.generate_context_pool(self.workload_config.num_contexts, self.workload_config.input_length)
        # we do a tiling pattern for context pool to maximize evictions between context reuse
        self.context_counter = 0
        self.question_pool = WorkloadGenerator.generate_question_pool(self.workload_config.questions_per_context)

        self.sem = asyncio.Semaphore(self.workload_config.max_inflight_requests)
        
    async def process_single_prompt(self, prompt: str):
        start_time = time.time()
        first_token_time = None

        try:
            response = await self.client.completions.create(
                model=self.workload_config.model_name,
                prompt=prompt,
                stream=True,
                max_tokens=self.workload_config.output_length,
            )

            pieces = []
            async for chunk in response:
                if not WorkloadGenerator.has_content(chunk):
                    continue
                content = WorkloadGenerator.extract_content(chunk)
                if first_token_time is None:
                    first_token_time = time.time()
                pieces.append(content)

            end_time = time.time()
            final_response = "".join(pieces)
            stat = RequestStats(
                start_time=start_time,
                first_token_time=first_token_time,
                end_time=end_time,
                input_length=len(prompt),
                output_length=len(final_response),
            )
            self.observability_panel.on_request_finished(stat)

        # --- handle specific errors ---
        except RateLimitError as e:
            print(f"[WARN] Rate limit hit: {e}. Use a stronger API key.")
            os._exit(1)
        except NotFoundError as e:
            print(f"[ERROR] Endpoint not found: {e}")
            os._exit(1)
        except AuthenticationError as e:
            print(f"[ERROR] Invalid API key or auth error: {e}")
            os._exit(1)
        except APIConnectionError as e:
            print(f"[ERROR] Connection issue: {e}")
            os._exit(1)
        except APIError as e:
            print(f"[ERROR] Generic API error: {e}")
            os._exit(1)
        except Exception as e:
            print(f"[ERROR] Unexpected exception: {e}")
            os._exit(1)

    async def infinitely_benchmark(self): 
        await self.observability_panel.start()
        while True: 
            await self.sem.acquire()
            context = self.context_pool[self.context_counter]
            self.context_counter = (self.context_counter + 1) % self.workload_config.num_contexts
            question = random.choice(self.question_pool)
            future = asyncio.create_task(self.process_single_prompt(context + question))
            future.add_done_callback(lambda _: self.sem.release())

def url_reduce(endpoint: str) -> str:
    """
    Normalize an OpenAI-style endpoint to a canonical base URL ending with /v1.
    The OpenAI SDK does NOT append /v1 automatically, so we ensure it's present.

    Works for:
      - Local servers (vLLM, LMCache):  http://localhost:8000/v1
      - Fireworks API:                   https://api.fireworks.ai/inference/v1
      - Generic OpenAI-style providers:  https://api.provider.com/v1
    """
    from urllib.parse import urlparse, urlunparse

    # Ensure scheme
    if not endpoint.startswith(("http://", "https://")):
        endpoint = "http://" + endpoint

    parsed = urlparse(endpoint)
    scheme = parsed.scheme
    netloc = parsed.netloc or parsed.path
    path = parsed.path or ""

    # Downgrade https→http only for localhost
    if scheme == "https" and netloc.startswith(("localhost", "127.0.0.1", "[::1]")):
        scheme = "http"

    # Always include exactly one /v1 at the end
    if "/v1" in path:
        normalized_path = path[: path.find("/v1") + len("/v1")]
    else:
        normalized_path = path.rstrip("/") + "/v1"

    # Strip any trailing slash inconsistencies
    normalized = urlunparse((scheme, netloc, normalized_path.rstrip("/"), "", "", ""))
    return normalized

def run_benchmark(args):
    endpoint = args.endpoint
    api_key = args.api_key
    print(f"endpoint: {endpoint}")
    print(f"api_key: {api_key}")
    endpoint = url_reduce(endpoint)
    print(f"normalized endpoint: {endpoint}")
    workload_config = WorkloadConfig.from_endpoint(endpoint, api_key)
    workload_generator = WorkloadGenerator(workload_config, endpoint, api_key)

    async def main():
        try:
            await workload_generator.infinitely_benchmark()
        except asyncio.CancelledError:
            print("\n[INFO] Cancelled benchmark tasks.")
        finally:
            print("[INFO] Benchmark stopped gracefully.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Define shutdown handler
    def handle_signal():
        print("\n[INFO] Received termination signal. Stopping benchmark...")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, handle_signal)
        except NotImplementedError:
            # Windows fallback
            signal.signal(sig, lambda s, f: asyncio.create_task(shutdown(loop)))

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt received. Exiting...")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()