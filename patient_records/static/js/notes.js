document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap modals
    const noteModal = document.getElementById('note-modal');
    const noteModalInstance = new bootstrap.Modal(noteModal);
    const quickViewModal = document.getElementById('noteQuickViewModal');
    const quickViewModalInstance = new bootstrap.Modal(quickViewModal);

    // Add event listeners for modal cleanup
    noteModal.addEventListener('hidden.bs.modal', function () {
        document.body.classList.remove('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        // Reset form on modal close
        resetForm();
    });

    quickViewModal.addEventListener('hidden.bs.modal', function () {
        document.body.classList.remove('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
    });

    // Initialize TinyMCE
    tinymce.init({
        selector: '#id_content',
        height: 300,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table paste code help wordcount',
            'codesample emoticons hr imagetools nonbreaking pagebreak quickbars',
            'fontselect fontsizeselect'
        ],
        toolbar: 'undo redo | formatselect | fontselect fontsizeselect | ' +
            'bold italic underline strikethrough | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist outdent indent | ' +
            'removeformat | help | link image media codesample | ' +
            'emoticons hr pagebreak | forecolor backcolor | subscript superscript | table',
        menubar: 'file edit view insert format tools table help',
        toolbar_mode: 'sliding',
        contextmenu: 'link image imagetools table',
        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
        font_formats: 'Arial=arial,helvetica,sans-serif; Courier New=courier new,courier,monospace; AkrutiKndPadmini=Akpdmi-n',
        fontsize_formats: '8pt 10pt 12pt 14pt 18pt 24pt 36pt',
        setup: function(editor) {
            editor.on('change', function() {
                editor.save();
            });
        },
        init_instance_callback: function(editor) {
            editor.on('submit', function(e) {
                e.preventDefault(); // Prevent TinyMCE's default submit behavior
            });
        }
    });

    // Handle New Note button clicks - using event delegation
    document.addEventListener('click', function(e) {
        const newNoteBtn = e.target.closest('#newNoteBtn, #emptyStateNewNote');
        if (newNoteBtn) {
            e.preventDefault();
            e.stopPropagation();
            
            resetForm();
            document.querySelector('#noteModalLabel').textContent = 'New Note';
            document.querySelector('.note-form').setAttribute('action', '/patient/notes/create/');
            document.querySelector('.modal-footer .btn-primary').textContent = 'Create Note';
            noteModalInstance.show();
        }
    });

    // Handle Edit Note
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-note')) {
            e.preventDefault();
            const noteId = e.target.closest('.edit-note').dataset.noteId;
            fetch(`/patient/notes/${noteId}/edit/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.querySelector('#noteModalLabel').textContent = 'Edit Note';
                        document.querySelector('.note-form').setAttribute('action', `/patient/notes/${noteId}/edit/`);
                        document.querySelector('.modal-footer .btn-primary').textContent = 'Save Changes';
                        
                        // Populate form fields
                        document.querySelector('#id_title').value = data.note.title;
                        document.querySelector('#id_category').value = data.note.category;
                        tinymce.get('id_content').setContent(data.note.content);
                        document.querySelector('#id_tags').value = data.note.tags.join(', ');
                        document.querySelector('#id_is_pinned').checked = data.note.is_pinned;
                        
                        noteModalInstance.show();
                    }
                });
        }
    });

    // Handle Delete Note with improved event handling
    const deleteNoteHandler = async function(noteId) {
        try {
            const response = await fetch(`/patient/notes/${noteId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            const data = await response.json();
            if (data.success) {
                const noteElement = document.querySelector(`[data-note-id="${noteId}"]`);
                if (noteElement) {
                    noteElement.remove();
                }
                const noteDetail = document.querySelector('#noteDetail');
                if (noteDetail) {
                    noteDetail.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-file-alt"></i>
                            <p>Select a note to view its contents</p>
                            <p class="text-muted">Or create a new note to get started</p>
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Error deleting note:', error);
            alert('Failed to delete note. Please try again.');
        }
    };

    document.addEventListener('click', function(e) {
        const deleteButton = e.target.closest('.delete-note');
        if (deleteButton) {
            // Stop event immediately
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation(); // This prevents other handlers from firing
            
            const noteId = deleteButton.dataset.noteId;
            if (window.confirm('Are you sure you want to delete this note?')) {
                deleteNoteHandler(noteId);
            }
        }
    });

    // Handle form submission
    const noteForm = document.querySelector('.note-form');
    if (noteForm) {
        noteForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Check if form is already being submitted
            if (this.hasAttribute('data-submitting') || this.getAttribute('data-submit-once') === 'submitted') {
                return;
            }
            
            // Mark form as being submitted
            this.setAttribute('data-submitting', 'true');
            this.setAttribute('data-submit-once', 'submitted');
            
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            }
            
            try {
                // Save TinyMCE content
                if (tinymce.get('id_content')) {
                    tinymce.get('id_content').save();
                }
                
                const formData = new FormData(this);
                
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Hide modal first
                    noteModalInstance.hide();
                    // Redirect to refresh the page
                    window.location.href = window.location.href;
                } else {
                    displayFormErrors(data.errors);
                    // Reset submission state on error
                    this.removeAttribute('data-submitting');
                    this.removeAttribute('data-submit-once');
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = 'Create Note';
                    }
                }
            } catch (error) {
                console.error('Error submitting note form:', error);
                alert('There was an error saving your note. Please try again.');
                // Reset submission state on error
                this.removeAttribute('data-submitting');
                this.removeAttribute('data-submit-once');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Create Note';
                }
            }
        });
        
        // Reset form submission state when modal is hidden
        noteModal.addEventListener('hidden.bs.modal', function() {
            const form = document.querySelector('.note-form');
            if (form) {
                form.removeAttribute('data-submitting');
                form.removeAttribute('data-submit-once');
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Create Note';
                }
            }
        });
    }

    // Helper function to reset form
    function resetForm() {
        const form = document.querySelector('.note-form');
        if (form) {
            form.reset();
            if (tinymce.get('id_content')) {
                tinymce.get('id_content').setContent('');
            }
            // Clear any previous error messages
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            form.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');
        }
    }

    // Display form errors
    function displayFormErrors(errors) {
        Object.keys(errors).forEach(field => {
            const input = document.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = input.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.textContent = errors[field].join(' ');
                }
            }
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle note item clicks for quick view
    document.addEventListener('click', function(e) {
        const noteItem = e.target.closest('.note-item');
        const actionButton = e.target.closest('.note-actions button');
        
        if (noteItem && !actionButton) {  // Only trigger if not clicking action buttons
            e.preventDefault();
            const noteId = noteItem.dataset.noteId;
            
            // Fetch note details
            fetch(`/patient/notes/${noteId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Populate quick view modal
                        const modal = document.getElementById('noteQuickViewModal');
                        modal.querySelector('.note-title').textContent = data.note.title;
                        modal.querySelector('.note-category .badge').textContent = data.note.category_display;
                        modal.querySelector('.note-content').innerHTML = data.note.content;
                        
                        // Handle pin indicator
                        const pinIcon = modal.querySelector('.fa-thumbtack');
                        if (data.note.is_pinned) {
                            if (!pinIcon) {
                                const icon = document.createElement('i');
                                icon.className = 'fas fa-thumbtack text-primary ms-2';
                                modal.querySelector('.modal-title').appendChild(icon);
                            }
                        } else if (pinIcon) {
                            pinIcon.remove();
                        }
                        
                        // Handle tags
                        const tagsContainer = modal.querySelector('.tags-container');
                        if (data.note.tags && data.note.tags.length > 0) {
                            tagsContainer.innerHTML = data.note.tags.map(tag => 
                                `<span class="note-tag">${tag}</span>`
                            ).join('');
                            tagsContainer.closest('.note-tags').style.display = 'block';
                        } else {
                            tagsContainer.closest('.note-tags').style.display = 'none';
                        }
                        
                        // Handle attachments
                        const attachmentsContainer = modal.querySelector('.attachments-container');
                        if (data.note.attachments && data.note.attachments.length > 0) {
                            attachmentsContainer.innerHTML = data.note.attachments.map(att => `
                                <div class="attachment-item">
                                    <i class="fas fa-paperclip"></i>
                                    <a href="${att.url}" target="_blank">${att.filename}</a>
                                </div>
                            `).join('');
                            attachmentsContainer.closest('.note-attachments').style.display = 'block';
                        } else {
                            attachmentsContainer.closest('.note-attachments').style.display = 'none';
                        }
                        
                        // Update meta information
                        modal.querySelector('.created-by').textContent = `Created by: ${data.note.created_by}`;
                        modal.querySelector('.last-edited').textContent = `Last edited: ${data.note.updated_at}`;
                        
                        // Show the modal
                        quickViewModalInstance.show();
                    }
                })
                .catch(error => {
                    console.error('Error fetching note details:', error);
                });
        }
    });
}); 