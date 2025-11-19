# a simple script to download the latest SDK package
import os
import boto3
import logging
from clearml import Dataset
from fastapi import HTTPException
from pathlib import Path
from data.sdk.download_sdk import s3_download


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    absolute_path = Path(__file__).parent / "downloaded_datasettt"
    dataset_name = "test_token"
    

    user_name = "datauserv3"

    # download

    s3_download(
        dataset_name=dataset_name,
        absolute_path=absolute_path,
        user_name=user_name,
        token="qazQAZ",
        clearml_api_host="http://144.172.105.98:30003",
        user_management_url="http://144.172.105.98:30009"
    )

    # presigned_urls method

    # url = s3_download(
    # clearml_access_key,
    # clearml_secret_key,
    # s3_access_key,
    # s3_secret_key,
    # s3_endpoint_url,
    # dataset_name,
    # absolute_path,
    # user_name,
    # method="presigned_urls")

    # print("Downloaded SDK package is available at:", url)

    # zip_streaming method

    # zip_data = s3_download_sdk(
    #     clearml_access_key,
    #     clearml_secret_key,
    #     s3_access_key,
    #     s3_secret_key,
    #     s3_endpoint_url,
    #     dataset_name,
    #     absolute_path,
    #     user_name,
    #     method="streaming_zip")

    # print(type(zip_data))
    # if zip_data:
    #     path = Path(__file__).parent / "dataset.zip"
    #     with open(path, "wb") as f:
    #         f.write(zip_data)
    #     print("Successfully saved dataset.zip")


if __name__ == "__main__":
    main()
