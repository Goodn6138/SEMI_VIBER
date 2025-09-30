export class FileTree {
  constructor(containerId, onFileSelect) {
    this.container = document.getElementById(containerId);
    this.onFileSelect = onFileSelect;
    this.files = new Map();
    this.expandedFolders = new Set();
  }

  setFiles(files) {
    this.files = new Map(files.map(f => [f.path, f]));
    this.render();
  }

  buildTree() {
    const tree = {};

    for (const [path, file] of this.files) {
      const parts = path.split('/');
      let current = tree;

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        const isFile = i === parts.length - 1;

        if (isFile) {
          current[part] = { type: 'file', data: file };
        } else {
          if (!current[part]) {
            current[part] = { type: 'folder', children: {} };
          }
          current = current[part].children;
        }
      }
    }

    return tree;
  }

  toggleFolder(folderPath) {
    if (this.expandedFolders.has(folderPath)) {
      this.expandedFolders.delete(folderPath);
    } else {
      this.expandedFolders.add(folderPath);
    }
    this.render();
  }

  renderNode(name, node, path = '') {
    const currentPath = path ? `${path}/${name}` : name;

    if (node.type === 'file') {
      const fileItem = document.createElement('div');
      fileItem.className = 'file-item';
      fileItem.innerHTML = `
        <span class="file-icon">${this.getFileIcon(name)}</span>
        <span>${name}</span>
      `;
      fileItem.addEventListener('click', () => {
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
        fileItem.classList.add('active');
        this.onFileSelect(node.data);
      });
      return fileItem;
    } else {
      const folderItem = document.createElement('div');
      folderItem.className = 'folder-item';

      const isExpanded = this.expandedFolders.has(currentPath);
      const icon = isExpanded ? '📂' : '📁';

      const folderHeader = document.createElement('div');
      folderHeader.className = 'folder-header';
      folderHeader.innerHTML = `
        <span class="folder-icon">${icon}</span>
        <span>${name}</span>
      `;
      folderHeader.addEventListener('click', () => this.toggleFolder(currentPath));

      folderItem.appendChild(folderHeader);

      if (isExpanded) {
        const childrenContainer = document.createElement('div');
        childrenContainer.className = 'folder-children';

        const sortedChildren = Object.entries(node.children).sort((a, b) => {
          const aIsFolder = a[1].type === 'folder';
          const bIsFolder = b[1].type === 'folder';
          if (aIsFolder && !bIsFolder) return -1;
          if (!aIsFolder && bIsFolder) return 1;
          return a[0].localeCompare(b[0]);
        });

        for (const [childName, childNode] of sortedChildren) {
          childrenContainer.appendChild(this.renderNode(childName, childNode, currentPath));
        }

        folderItem.appendChild(childrenContainer);
      }

      return folderItem;
    }
  }

  getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
      'js': '📜',
      'py': '🐍',
      'html': '🌐',
      'css': '🎨',
      'json': '📋',
      'md': '📝',
      'txt': '📄',
      'gitignore': '🚫',
      'env': '🔐'
    };
    return iconMap[ext] || '📄';
  }

  render() {
    if (this.files.size === 0) {
      this.container.innerHTML = `
        <div style="padding: 12px; color: #858585; font-size: 13px;">
          No files loaded. Generate code to see files.
        </div>
      `;
      return;
    }

    this.container.innerHTML = '';
    const tree = this.buildTree();

    const sortedRoot = Object.entries(tree).sort((a, b) => {
      const aIsFolder = a[1].type === 'folder';
      const bIsFolder = b[1].type === 'folder';
      if (aIsFolder && !bIsFolder) return -1;
      if (!aIsFolder && bIsFolder) return 1;
      return a[0].localeCompare(b[0]);
    });

    for (const [name, node] of sortedRoot) {
      this.container.appendChild(this.renderNode(name, node));
    }
  }
}