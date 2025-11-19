class S3Downloader:

    def download(self, dataset_id, target, prefix=None, key=None, jobs=4, debug=False, runtime="ks3util"):
        from ..core.baai_share_url import download_share


        download_share(dataset, save_path, prefix, key, jobs_down, debug)



def new_downloader(ak, sk, runtime="ks3util"):
    from ..baai_config import config_update
    from ..baai_environment import setup_network

    config_update({
        "ak": ak,
        "sk": sk,
    })

    setup_network()


    return S3Downloader()