// 聊天界面配置文件
const ChatConfig = {
    // 工具按钮配置
    toolButtons: [
        {
            id: 'clearBtn',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18"></path>
                <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
            </svg>`,
            label: '清空',
            title: '清空聊天',
            action: 'clearChat',
            visible: true
        },
        {
            id: 'saveBtn',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                <polyline points="17,21 17,13 7,13 7,21"></polyline>
                <polyline points="7,3 7,8 15,8"></polyline>
            </svg>`,
            label: '保存',
            title: '保存聊天记录',
            action: 'saveChat',
            visible: true
        },
        {
            id: 'settingsBtn',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1"></path>
            </svg>`,
            label: '设置',
            title: '设置',
            action: 'openSettings',
            visible: true
        },
        {
            id: 'helpBtn',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`,
            label: '帮助',
            title: '帮助',
            action: 'showHelp',
            visible: true
        },
        {
            id: 'exportBtn',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
            </svg>`,
            label: '导出',
            title: '导出为Markdown',
            action: 'exportAsMarkdown',
            visible: true
        },
        // 你可以添加更多自定义按钮
        {
            id: 'customBtn1',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13,2 3,14 12,14 11,22 21,10 12,10"></polygon>
            </svg>`,
            label: '快速回复',
            title: '快速回复模板',
            action: 'showQuickReplies',
            visible: false // 默认隐藏，可通过设置启用
        },
        {
            id: 'customBtn2',
            icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21,15 16,10 5,21"></polyline>
            </svg>`,
            label: '图片',
            title: '发送图片',
            action: 'sendImage',
            visible: false // 默认隐藏，可通过设置启用
        }
    ],
    
    // 主题配置
    themes: {
        light: {
            name: '浅色主题',
            primary: '#667eea',
            secondary: '#764ba2',
            background: '#ffffff',
            surface: '#f8f9fa',
            text: '#333333'
        },
        dark: {
            name: '深色主题', 
            primary: '#667eea',
            secondary: '#764ba2',
            background: '#1a1a1a',
            surface: '#2d2d2d',
            text: '#ffffff'
        }
    },
    
    // Markdown配置
    markdown: {
        breaks: true,
        gfm: true,
        highlight: true,
        linkify: true
    },
    
    // 默认设置
    defaultSettings: {
        theme: 'light',
        fontSize: 'medium',
        autoScroll: true,
        enableNotifications: true,
        maxMessages: 1000
    },
    
    // 快速回复模板
    quickReplies: [
        '好的，我明白了',
        '感谢您的回复',
        '请稍等片刻',
        '有什么其他问题吗？',
        '需要更多帮助吗？'
    ],
    
    // 自定义CSS变量
    cssVariables: {
        '--chat-primary-color': '#667eea',
        '--chat-secondary-color': '#764ba2',
        '--chat-border-radius': '18px',
        '--chat-shadow': '0 2px 8px rgba(0,0,0,0.1)',
        '--chat-transition': '0.2s ease'
    }
};

// 如果在浏览器环境中，将配置添加到全局
if (typeof window !== 'undefined') {
    window.ChatConfig = ChatConfig;
}

// 如果在Node.js环境中，导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatConfig;
}