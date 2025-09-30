import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { oneDark } from '@codemirror/theme-one-dark';

export class CodeEditor {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.tabsBar = document.getElementById('tabs-bar');
    this.openFiles = new Map();
    this.currentFile = null;
    this.editorView = null;
  }

  getLanguageSupport(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const langMap = {
      'js': javascript(),
      'jsx': javascript({ jsx: true }),
      'ts': javascript({ typescript: true }),
      'tsx': javascript({ typescript: true, jsx: true }),
      'py': python(),
      'html': html(),
      'css': css()
    };
    return langMap[ext] || javascript();
  }

  openFile(file) {
    if (!this.openFiles.has(file.path)) {
      this.openFiles.set(file.path, file);
      this.renderTabs();
    }
    this.switchToFile(file.path);
  }

  closeFile(filePath) {
    this.openFiles.delete(filePath);

    if (this.currentFile === filePath) {
      const files = Array.from(this.openFiles.keys());
      if (files.length > 0) {
        this.switchToFile(files[files.length - 1]);
      } else {
        this.currentFile = null;
        this.destroyEditor();
        this.showPlaceholder();
      }
    }

    this.renderTabs();
  }

  switchToFile(filePath) {
    const file = this.openFiles.get(filePath);
    if (!file) return;

    this.currentFile = filePath;
    this.renderTabs();
    this.renderEditor(file);
  }

  renderTabs() {
    this.tabsBar.innerHTML = '';

    for (const [path, file] of this.openFiles) {
      const tab = document.createElement('div');
      tab.className = 'tab';
      if (path === this.currentFile) {
        tab.classList.add('active');
      }

      const filename = path.split('/').pop();
      tab.innerHTML = `
        <span>${filename}</span>
        <span class="tab-close">×</span>
      `;

      tab.addEventListener('click', (e) => {
        if (e.target.classList.contains('tab-close')) {
          e.stopPropagation();
          this.closeFile(path);
        } else {
          this.switchToFile(path);
        }
      });

      this.tabsBar.appendChild(tab);
    }
  }

  destroyEditor() {
    if (this.editorView) {
      this.editorView.destroy();
      this.editorView = null;
    }
  }

  showPlaceholder() {
    this.container.innerHTML = `
      <div class="editor-placeholder">
        Select a file to view its contents
      </div>
    `;
  }

  renderEditor(file) {
    this.destroyEditor();
    this.container.innerHTML = '';

    const state = EditorState.create({
      doc: file.content,
      extensions: [
        basicSetup,
        this.getLanguageSupport(file.path),
        oneDark,
        EditorView.theme({
          "&": { height: "100%" },
          ".cm-scroller": { overflow: "auto" }
        })
      ]
    });

    this.editorView = new EditorView({
      state,
      parent: this.container
    });
  }

  getCurrentFileContent() {
    if (!this.editorView) return null;
    return this.editorView.state.doc.toString();
  }
}