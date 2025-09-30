import { signUp, signIn, signOut, getCurrentUser, onAuthStateChange, getUserSettings, saveUserSettings } from './auth.js';
import { FileTree } from './fileTree.js';
import { CodeEditor } from './editor.js';

const BACKEND_URL = 'https://semi-viber.onrender.com';

let currentUser = null;
let userSettings = null;

const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');
const loadingOverlay = document.getElementById('loading-overlay');
const statusText = document.getElementById('status-text');
const userEmailSpan = document.getElementById('user-email');

const authEmail = document.getElementById('auth-email');
const authPassword = document.getElementById('auth-password');
const authSignInBtn = document.getElementById('auth-signin-btn');
const authSignUpBtn = document.getElementById('auth-signup-btn');
const authError = document.getElementById('auth-error');

const settingsModal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const settingsClose = document.getElementById('settings-close');
const settingsCancel = document.getElementById('settings-cancel');
const settingsSave = document.getElementById('settings-save');
const githubTokenInput = document.getElementById('github-token');
const openaiKeyInput = document.getElementById('openai-key');

const runCodeBtn = document.getElementById('run-code-btn');
const generateBtn = document.getElementById('generate-btn');

const editor = new CodeEditor('editor-content');
const fileTree = new FileTree('file-tree', (file) => {
  editor.openFile(file);
});

function showLoading() {
  loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
  loadingOverlay.classList.add('hidden');
}

function setStatus(text) {
  statusText.textContent = text;
}

function showError(message) {
  authError.textContent = message;
  authError.style.display = 'block';
}

function hideError() {
  authError.style.display = 'none';
}

async function handleSignIn() {
  const email = authEmail.value.trim();
  const password = authPassword.value;

  if (!email || !password) {
    showError('Please enter email and password');
    return;
  }

  try {
    showLoading();
    hideError();
    await signIn(email, password);
  } catch (error) {
    showError(error.message);
  } finally {
    hideLoading();
  }
}

async function handleSignUp() {
  const email = authEmail.value.trim();
  const password = authPassword.value;

  if (!email || !password) {
    showError('Please enter email and password');
    return;
  }

  if (password.length < 6) {
    showError('Password must be at least 6 characters');
    return;
  }

  try {
    showLoading();
    hideError();
    await signUp(email, password);
    showError('Account created! Please sign in.');
  } catch (error) {
    showError(error.message);
  } finally {
    hideLoading();
  }
}

async function loadUserSettings() {
  try {
    userSettings = await getUserSettings();
    if (userSettings) {
      githubTokenInput.value = userSettings.github_token || '';
      openaiKeyInput.value = userSettings.openai_api_key || '';
    }
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

async function handleSaveSettings() {
  const githubToken = githubTokenInput.value.trim();
  const openaiKey = openaiKeyInput.value.trim();

  try {
    showLoading();
    await saveUserSettings({
      github_token: githubToken,
      openai_api_key: openaiKey
    });
    userSettings = { github_token: githubToken, openai_api_key: openaiKey };
    settingsModal.classList.add('hidden');
    setStatus('Settings saved successfully');
  } catch (error) {
    alert('Error saving settings: ' + error.message);
  } finally {
    hideLoading();
  }
}

async function handleRunCode() {
  const content = editor.getCurrentFileContent();
  if (!content) {
    alert('No file is open in the editor');
    return;
  }

  try {
    showLoading();
    setStatus('Running code...');

    const response = await fetch(`${BACKEND_URL}/run-code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code: content })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    alert('Results:\n\n' + data.results);
    setStatus('Code executed successfully');
  } catch (error) {
    console.error('Error running code:', error);
    alert('Error: ' + error.message);
    setStatus('Error running code');
  } finally {
    hideLoading();
  }
}

async function handleGenerate() {
  const description = prompt('Enter a description of the code you want to generate:');

  if (!description) {
    return;
  }

  try {
    showLoading();
    setStatus('Generating code...');

    const response = await fetch(`${BACKEND_URL}/generate-code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      alert('Code generated successfully!\n\nRepository: ' + data.repoUrl);

      if (data.generatedCode) {
        const mockFiles = [
          { path: 'main.py', content: data.generatedCode },
          { path: 'README.md', content: '# Generated Project\n\n' + data.folderStructure }
        ];
        fileTree.setFiles(mockFiles);
      }

      setStatus('Code generated successfully');
    } else {
      throw new Error(data.error || 'Failed to generate code');
    }
  } catch (error) {
    console.error('Error generating code:', error);
    alert('Error: ' + error.message);
    setStatus('Error generating code');
  } finally {
    hideLoading();
  }
}

authSignInBtn.addEventListener('click', handleSignIn);
authSignUpBtn.addEventListener('click', handleSignUp);
authEmail.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleSignIn();
});
authPassword.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') handleSignIn();
});

settingsBtn.addEventListener('click', () => {
  settingsModal.classList.remove('hidden');
});

settingsClose.addEventListener('click', () => {
  settingsModal.classList.add('hidden');
});

settingsCancel.addEventListener('click', () => {
  settingsModal.classList.add('hidden');
});

settingsSave.addEventListener('click', handleSaveSettings);

runCodeBtn.addEventListener('click', handleRunCode);
generateBtn.addEventListener('click', handleGenerate);

settingsModal.addEventListener('click', (e) => {
  if (e.target === settingsModal) {
    settingsModal.classList.add('hidden');
  }
});

onAuthStateChange(async (event, session) => {
  if (session?.user) {
    currentUser = session.user;
    userEmailSpan.textContent = currentUser.email;
    authContainer.classList.add('hidden');
    appContainer.classList.remove('hidden');
    await loadUserSettings();
    setStatus('Ready');
  } else {
    currentUser = null;
    appContainer.classList.add('hidden');
    authContainer.classList.remove('hidden');
    setStatus('Not authenticated');
  }
});

(async () => {
  const user = await getCurrentUser();
  if (user) {
    currentUser = user;
    userEmailSpan.textContent = currentUser.email;
    appContainer.classList.remove('hidden');
    await loadUserSettings();
    setStatus('Ready');
  } else {
    authContainer.classList.remove('hidden');
  }
})();