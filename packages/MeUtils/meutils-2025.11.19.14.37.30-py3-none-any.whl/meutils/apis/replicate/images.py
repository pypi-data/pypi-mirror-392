#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : images
# @Time         : 2025/11/18 16:29
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.schemas.image_types import ImageRequest, ImagesResponse

import replicate


client = replicate.client.Client(api_token="r8_9z6XZKztr3InGJwKjxRuIFTU4xsyKZl1yss5y")


async def generate(request: ImageRequest):
    output = await client.async_run(
        "flux-kontext-apps/multi-image-kontext-pro",
        input={
            "prompt": image_request.prompt,
            "aspect_ratio": image_request.aspect_ratio,
            "input_image_1": image_request.input_image_1,
            "input_image_2": image_request.input_image_2,
            "output_format": image_request.output_format,
            "safety_tolerance": image_request.safety_tolerance
        }
    )

    return ImagesResponse(images=output.url)

# output = client.run(
#     "flux-kontext-apps/multi-image-kontext-pro",
#     input={
#         "prompt": "Put the woman next to the house",
#         "aspect_ratio": "match_input_image",
#         "input_image_1": "https://replicate.delivery/pbxt/N7gRAUNcVF6HarL0hdAQA2JYNMlJD52LP1wyaIWRUXWeHzqT/0_1-1.webp",
#         "input_image_2": "https://replicate.delivery/pbxt/N7gRAK5kbPwdsbOpqgyAIOFQX45U6suTlbL6ws2N74SnGFpo/test.jpg",
#         "output_format": "png",
#         "safety_tolerance": 2
#     }
# )

output = client.async_run(
    "flux-kontext-apps/multi-image-kontext-pro",
    input={
        "prompt": "Put the woman next to the house",
        "aspect_ratio": "match_input_image",
        "input_image_1": "https://replicate.delivery/pbxt/N7gRAUNcVF6HarL0hdAQA2JYNMlJD52LP1wyaIWRUXWeHzqT/0_1-1.webp",
        "input_image_2": "https://replicate.delivery/pbxt/N7gRAK5kbPwdsbOpqgyAIOFQX45U6suTlbL6ws2N74SnGFpo/test.jpg",
        "output_format": "png",
        "safety_tolerance": 2
    }
)


# To access the file URL:
# print(output.url)
#=> "http://example.com"

if __name__ == '__main__':
    image_request = ImageRequest(
        prompt="Put the woman next to the house",
        aspect_ratio="match_input_image",
        input_image_1="https://replicate.delivery/pbxt/N7gRAUNcVF6HarL0hdAQA2JYNMlJD52LP1wyaIWRUXWeHzqT/0_1-1.webp",
        input_image_2="https://replicate.delivery/pbxt/N7gRAK5kbPwdsbOpqgyAIOFQX45U6suTlbL6ws2N74SnGFpo/test.jpg",
        output_format="png",
        safety_tolerance=2
    )

    arun(output)