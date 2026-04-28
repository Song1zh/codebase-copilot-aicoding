def upload_file(file_path: str) -> dict:
    # Bug: empty file_path is not handled explicitly.
    if file_path is None:
        return {"status": "error", "message": "file_path is required"}

    with open(file_path, "rb") as f:
        data = f.read()

    return {
        "status": "ok",
        "size": len(data),
    }