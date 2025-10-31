document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const submitCorrectionButton = document.getElementById('submit-correction');
    const correctionDropdown = document.getElementById('correction-dropdown');
    const animalClassesList = document.getElementById('animal-classes-list');
    const imageUpload = document.getElementById('image-upload');
    const predictButton = document.getElementById('predict-button');
    const resultContainer = document.getElementById('result-container');
    const feedbackCard = document.getElementById('feedback-card');
    const feedbackReceivedAlert = document.getElementById('feedback-received-alert');
    const showFeedbackBtn = document.getElementById('show-feedback-btn');
    const uploadArea = document.getElementById('upload-area');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const copyBreedBtn = document.getElementById('copy-breed-btn');
    const toastContainer = document.getElementById('toast-container');

    // Prediction display elements
    const classEmoji = document.getElementById('class-emoji');
    const mainClassLabel = document.getElementById('main-class-label');
    const breedDisplay = document.getElementById('breed-display');
    const breedName = document.getElementById('breed-name');
    const confidenceText = document.getElementById('confidence-text');

    let animalClasses = [];
    let currentBreedName = '';

    // Animal emoji mapping
    const animalEmojis = {
        'Dog': '🐶',
        'Cat': '🐱',
        'Bird': '🐦',
        'Bear': '🐻',
        'Lion': '🦁',
        'Tiger': '🐯',
        'Elephant': '🐘',
        'Giraffe': '🦒',
        'Horse': '🐎',
        'Cow': '🐮',
        'Deer': '🦌',
        'Dolphin': '🐬',
        'Kangaroo': '🦘',
        'Panda': '🐼',
        'Zebra': '🦓',
        'Penguin': '🐧',
        'Owl': '🦉',
        'Eagle': '🦅',
        'Parrot': '🦜',
        'Swan': '🦢',
        'Duck': '🦆',
        'Crow': '🐦',
        'Sparrow': '🐦',
        'Hummingbird': '🐦',
        'Woodpecker': '🐦',
        'Kingfisher': '🐦',
        'Falcon': '🦅',
        'Ostrich': '🦃',
        'Pigeon': '🕊️',
        'Swallow': '🐦',
        'Cuckoo': '🐦'
    };

    // Toast notification system
    function showToast(message, type = 'info', duration = 4000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }

    // Fetch classes from backend
    async function loadClassOptions() {
        try {
            const res = await fetch('/classes');
            const data = await res.json();
            animalClasses = data.classes || [];
            populateClassDropdowns();
        } catch (error) {
            console.error("Error loading class options:", error);
            showToast('Failed to load animal classes', 'error');
        }
    }

    // Populate dropdowns
    function populateClassDropdowns() {
        correctionDropdown.innerHTML = '<option value="">Select correct class...</option>';

        animalClasses.forEach((animal) => {
            const displayName = animal.replace(/_/g, ' ');
            const option = document.createElement('option');
            option.value = animal;
            option.textContent = displayName;
            correctionDropdown.appendChild(option);
        });
    }

    // Get emoji for animal class
    function getAnimalEmoji(className) {
        const baseClass = getBaseClass(className);
        return animalEmojis[baseClass] || '🐾';
    }

    // Get base class from full class name
    function getBaseClass(className) {
        const cleanName = className.replace(/_/g, ' ');
        for (const [baseClass, emoji] of Object.entries(animalEmojis)) {
            if (cleanName.includes(baseClass)) {
                return baseClass;
            }
        }
        return cleanName.split(' ')[0];
    }

    // Handle image upload
    function handleImageUpload(file) {
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            showToast('Please select a valid image file', 'error');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            showToast('Image size must be less than 10MB', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('d-none');
            uploadArea.classList.add('d-none');
            predictButton.disabled = false;

            // Animate in the preview
            imagePreviewContainer.style.animation = 'slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
        };
        reader.readAsDataURL(file);
    }

    // Remove image
    window.removeImage = function () {
        imageUpload.value = '';
        imagePreviewContainer.classList.add('d-none');
        uploadArea.classList.remove('d-none');
        predictButton.disabled = true;
        resultContainer.classList.add('d-none');

        // Reset animations
        imagePreviewContainer.style.animation = '';
    };

    // Animated prediction display
    async function displayPrediction(result) {
        const baseClass = getBaseClass(result.prediction);
        const emoji = getAnimalEmoji(result.prediction);
        const confidence = (result.confidence * 100).toFixed(1);

        // Reset display
        resultContainer.classList.remove('d-none');
        breedDisplay.classList.add('d-none');
        copyBreedBtn.classList.add('d-none');

        // Show main class with animation
        classEmoji.textContent = emoji;
        mainClassLabel.textContent = baseClass;

        // Wait for main class animation, then show breed
        setTimeout(() => {
            if (result.breeds && result.breeds.length > 0) {
                currentBreedName = result.breeds[0];
                breedName.textContent = currentBreedName;
                confidenceText.textContent = `Confidence: ${confidence}%`;
                breedDisplay.classList.remove('d-none');
                copyBreedBtn.classList.remove('d-none');
            }
        }, 1500);

        showFeedbackBtn.classList.remove('d-none');
        window.currentPrediction = result.prediction;
    }

    // Copy breed name to clipboard
    copyBreedBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(currentBreedName);
            copyBreedBtn.classList.add('copy-success');
            copyBreedBtn.innerHTML = '<i class="bi bi-check me-1"></i>Copied!';
            showToast('Breed name copied to clipboard', 'success', 2000);

            setTimeout(() => {
                copyBreedBtn.classList.remove('copy-success');
                copyBreedBtn.innerHTML = '<i class="bi bi-clipboard me-1"></i>Copy Breed';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy breed name', 'error');
        }
    });

    // Image upload event
    imageUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleImageUpload(file);
    });

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            imageUpload.files = e.dataTransfer.files;
            handleImageUpload(file);
        } else {
            showToast('Please drop a valid image file', 'error');
        }
    });

    // Click to upload
    uploadArea.addEventListener('click', () => {
        imageUpload.click();
    });

    // Prediction handler
    predictButton.addEventListener('click', async () => {
        const imageFile = imageUpload.files[0];
        if (!imageFile) {
            showToast('Please upload an image first', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', imageFile);

        predictButton.disabled = true;
        predictButton.innerHTML = '<span class="loading me-2"></span>Analyzing...';

        try {
            const res = await fetch('/predict', { method: 'POST', body: formData });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const result = await res.json();

            if (result.error) {
                throw new Error(result.error);
            }

            await displayPrediction(result);
            showToast('Analysis completed successfully', 'success');
        } catch (err) {
            console.error('Prediction error:', err);

            // Show error in prediction card
            classEmoji.textContent = '❌';
            mainClassLabel.textContent = 'Error';
            breedDisplay.classList.remove('d-none');
            breedName.textContent = 'Failed to analyze image';
            confidenceText.textContent = 'Please try again';
            resultContainer.classList.remove('d-none');

            showToast('Failed to analyze image. Please try again.', 'error');
        } finally {
            predictButton.disabled = false;
            predictButton.innerHTML = '<i class="bi bi-search me-2"></i>Analyze Image';
        }
    });

    // Feedback submit
    submitCorrectionButton.addEventListener('click', async () => {
        const corrected = correctionDropdown.value;
        const imageFile = imageUpload.files[0];

        if (!corrected) {
            showToast('Please select a correct class', 'error');
            return;
        }

        if (!imageFile) {
            showToast('No image to submit feedback for', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('predicted', window.currentPrediction || 'Unknown');
        formData.append('actual', corrected);

        submitCorrectionButton.disabled = true;
        submitCorrectionButton.innerHTML = '<span class="loading me-2"></span>Submitting...';

        try {
            const res = await fetch('/feedback', { method: 'POST', body: formData });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const result = await res.json();

            showToast(result.message, 'success');
            feedbackCard.classList.remove('show');
            submitCorrectionButton.innerHTML = '<i class="bi bi-check me-1"></i>Submitted!';

            setTimeout(() => {
                submitCorrectionButton.innerHTML = '<i class="bi bi-check me-1"></i>Submit Correction';
                submitCorrectionButton.disabled = false;
            }, 3000);
        } catch (e) {
            console.error('Feedback error:', e);
            showToast('Error submitting feedback. Please try again.', 'error');
            submitCorrectionButton.innerHTML = '<i class="bi bi-check me-1"></i>Submit Correction';
            submitCorrectionButton.disabled = false;
        }
    });

    // Toggle feedback
    showFeedbackBtn.addEventListener('click', () => {
        new bootstrap.Collapse(feedbackCard, { toggle: true });
    });

    // Add slideOutRight animation for toast removal
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100%);
            }
        }
    `;
    document.head.appendChild(style);

    // Initialize
    loadClassOptions();
});
