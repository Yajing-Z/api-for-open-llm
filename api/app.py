import argparse
import json
import os
import sys

sys.path.insert(0, '.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OpenAI Compatible RESTful API server."
    )
    # fastapi related
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="host name"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="port number"
    )
    parser.add_argument(
        "--allow-credentials", action="store_true", help="allow credentials"
    )
    parser.add_argument(
        "--allowed-origins", type=json.loads, default=["*"], help="allowed origins"
    )
    parser.add_argument(
        "--allowed-methods", type=json.loads, default=["*"], help="allowed methods"
    )
    parser.add_argument(
        "--allowed-headers", type=json.loads, default=["*"], help="allowed headers"
    )

    # model related
    parser.add_argument(
        '--model_name', type=str, help='chatglm, moss, phoenix', default='chatglm'
    )
    parser.add_argument(
        '--model_path', '-m', type=str, help='model_name_or_path', default=None
    )
    parser.add_argument(
        '--adapter_model_path', type=str, help='lora or ptuing-v2 model_name_or_path', default=None
    )
    parser.add_argument(
        "--device", type=str, choices=["cpu", "cuda"], default="cuda", help="The device type"
    )
    parser.add_argument(
        "--gpus", type=str, default=None, help="A single GPU like 1 or multiple GPUs like 0,2"
    )
    parser.add_argument(
        "--num_gpus", type=int, default=1, help="Number of GPUs to use"
    )
    parser.add_argument(
        '--quantize', '-q', help='quantize, optional: 16，8，4', type=int, default=16
    )
    parser.add_argument(
        '--embedding_name', help='embedding model name or path', type=str, default=None
    )
    parser.add_argument(
        '--context_len', help='context length for generation', type=int, default=None
    )
    parser.add_argument(
        '--load_in_8bit', action='store_true', help='load in 8 bit'
    )
    parser.add_argument(
        '--load_in_4bit', action='store_true', help='load in 4 bit'
    )
    parser.add_argument(
        "--use_ptuning_v2", action="store_true", help='use ptuning v2 method for chatglm'
    )
    parser.add_argument(
        "--stream_interval", type=int, default=2, help='interval for stream output'
    )
    parser.add_argument(
        '--prompt_name', type=str, default=None, help="The prompt name for convasation. "
    )

    # patches related
    parser.add_argument(
        '--patch_type', type=str, default=None, choices=["rerope", "ntk"], help="The method to extend context length."
    )
    parser.add_argument(
        '--training_length', type=int, default=4096, help="The training length of NTK or ReRoPE method."
    )
    parser.add_argument(
        '--window_size', type=int, default=512, help="The window size of ReRoPE method."
    )
    args = parser.parse_args()
    sys.path.insert(0, args.model_path)

    if args.gpus:
        # logger.info(f"load model in GPUs = {args.gpus}")
        if len(args.gpus.split(",")) < args.num_gpus:
            raise ValueError(
                f"Larger --num_gpus ({args.num_gpus}) than --gpus {args.gpus}!"
            )
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus

    from api.router import main

    if args.patch_type == "rerope":
        from api.patches import apply_rerope_patch

        apply_rerope_patch(args.training_length, args.window_size)
    elif args.patch_type == "ntk":
        from api.patches import apply_ntk_scaling_patch

        apply_ntk_scaling_patch(args.training_length)

    main(args)
