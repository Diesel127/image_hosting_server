// Frontend logic for the upload page (`/upload`).
// Responsibilities:
// - Validate drag&drop / selected files and upload them to `/upload` (backend).
// - Show success/error messages.
// - After a successful upload, store an entry in `localStorage` so the images
//   list can render without fetching metadata again.
document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' || event.key === 'F5') {
            // Quick navigation back to home (Escape/F5 used as a shortcut here).
            event.preventDefault();
            window.location.href = '/';
        }
    });

    const fileUpload = document.getElementById('file-upload');
    const imagesButton = document.getElementById('images-tab-btn');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');

    if (imagesButton) {
        // Switch to the images list.
        imagesButton.addEventListener('click', () => window.location.href = '/images-list');
    }

    const showMessage = (message, isError = false) => {
        // Create a message element once and reuse it.
        let msgEl = document.querySelector('.upload__message');
        if (!msgEl) {
            msgEl = document.createElement('p');
            msgEl.className = 'upload__message';
            dropzone?.parentNode?.insertBefore(msgEl, dropzone.nextSibling);
        }
        msgEl.textContent = message;
        msgEl.style.color = isError ? '#e53e3e' : '#38a169';
    };

    const uploadFile = async (file) => {
        // Upload a single file to the backend.
        // The backend returns { success, filename, url, message } (JSON).
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Keep a lightweight client-side list for UI rendering.
                const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];

                const getNextImageNumber = () =>
                    storedFiles.filter(f => f.displayName && f.displayName.startsWith('image')).length + 1;

                const ext = file.name.substring(file.name.lastIndexOf('.'));
                const displayName = `image${String(getNextImageNumber()).padStart(2, '0')}${ext}`;

                const reader = new FileReader();
                reader.onload = (event) => {
                    // Store a local DataURL thumbnail so the list can display an image.
                    storedFiles.push({
                        name: data.filename,
                        displayName: displayName,
                        originalName: file.name,
                        url: event.target.result
                    });
                    localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                };
                reader.readAsDataURL(file);

                if (currentUploadInput) {
                    // Show a direct URL for the last uploaded file.
                    currentUploadInput.value = `https://image-hosting-server.com/${data.filename}`;
                }
                showMessage('File uploaded successfully!');
            } else {
                showMessage(data.message || 'Upload failed.', true);
            }
        } catch (err) {
            showMessage('Something went wrong. Please try again.', true);
        }
    };

    const handleAndStoreFiles = (files) => {
        // Upload all selected files sequentially (await inside uploadFile).
        if (!files || files.length === 0) return;
        for (const file of files) {
            uploadFile(file);
        }
    };

    if (copyButton && currentUploadInput) {
        // Copy the current URL from the readonly input to clipboard.
        copyButton.addEventListener('click', () => {
            const textToCopy = currentUploadInput.value;
            if (textToCopy && textToCopy !== 'https://') {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyButton.textContent = 'COPIED!';
                    setTimeout(() => copyButton.textContent = 'COPY', 2000);
                }).catch(err => console.error('Failed to copy text: ', err));
            }
        });
    }

    if (fileUpload) {
        fileUpload.addEventListener('change', (event) => {
            // User selected files via the file picker.
            handleAndStoreFiles(event.target.files);
            event.target.value = '';
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                // Prevent the browser from opening dragged files.
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropzone.addEventListener('dragover', () => dropzone.classList.add('dragover'));
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (event) => {
            dropzone.classList.remove('dragover');
            // Handle dropped files.
            handleAndStoreFiles(event.dataTransfer.files);
        });
    }
});
