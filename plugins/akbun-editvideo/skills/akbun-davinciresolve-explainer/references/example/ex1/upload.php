<?php
// upload.php - 업로드 크기 확인 예제
declare(strict_types=1);

const MAX_BYTES = 2 * 1024 * 1024;

function check_upload(array $file): string
{
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return 'upload failed';
    }
    if ($file['size'] > MAX_BYTES) {
        return 'too large';
    }
    return 'ok';
}

echo check_upload($_FILES['photo']);
