export function getFileIconClass(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const imageExts = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'];
    const videoExts = ['mp4', 'mkv', 'avi', 'mov'];
    const docExts = ['pdf', 'doc', 'docx', 'txt', 'md'];
    const codeExts = ['js', 'py', 'html', 'css', 'json'];

    if (imageExts.includes(ext)) return 'ph-image';
    if (videoExts.includes(ext)) return 'ph-video-camera';
    if (docExts.includes(ext)) return 'ph-file-text';
    if (codeExts.includes(ext)) return 'ph-file-code';
    if (['zip', 'rar', 'tar', 'gz'].includes(ext)) return 'ph-file-archive';

    return 'ph-file';
}
