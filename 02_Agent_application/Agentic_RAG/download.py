from huggingface_hub import snapshot_download

# 把 user/model-name 改成你的 repo ID
snapshot_download(
    repo_id="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir="./model",                    # 存到本機資料夾
)