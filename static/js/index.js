document.addEventListener('DOMContentLoaded', function () {
    // 重新进入后隐藏Loading动画
    hideLoading();

    // 从本地存储加载历史表单数据
    loadFormData();

    // 高级选项切换的事件设置
    setupAdvancedOptions();

    // 准实时保存输入参数
    setupRealTimeSave();

    // 绑定表单提交事件
    const form = document.getElementById('merge-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }

    // 离开时要进行
    window.addEventListener('beforeunload', handleBeforeLeave);

    // 添加CSS动画关键帧
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});

/**
 * 实时保存表单数据（在输入时实时保存）
 */
function setupRealTimeSave() {
    // 获取表单
    const form = document.getElementById('merge-form');
    if (!form) {
        return;
    }

    // 获取表单inputs，添加保存和防抖事件
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function () {
            // 防抖处理，避免频繁保存
            clearTimeout(window.saveTimeout);
            window.saveTimeout = setTimeout(saveFormData, 1000);
        });
    });
}

/**
 * 从localStorage加载表单数据
 */
function loadFormData() {
    try {
        const savedData = localStorage.getItem('gitlabMergeFormData');
        if (savedData) {
            // 解析历史数据
            const formData = JSON.parse(savedData);

            // 填充表单字段
            document.getElementById('source_branch').value = formData.source_branch || '';
            document.getElementById('target_branch').value = formData.target_branch || '';
            document.getElementById('start_with').value = formData.start_with || '';
            document.getElementById('reviewer_usernames').value = formData.reviewer_usernames || '';
            document.getElementById('assignee_usernames').value = formData.assignee_usernames || '';

            // 显示存储提示
            const storageNotice = document.getElementById('storage-notice');
            if (storageNotice) {
                storageNotice.style.display = 'flex';
            }
            console.log('✅ 表单数据已从localStorage加载成功', JSON.stringify(formData));
        }
    } catch (error) {
        console.error('❌ 加载本地存储数据失败:', error);
    }
}

/**
 * 保存表单数据到localStorage（在表单提交时调用）
 */
function saveFormData() {
    try {
        const sourceBranch = document.getElementById('source_branch');
        const targetBranch = document.getElementById('target_branch');
        const startWith = document.getElementById('start_with');
        const reviewerUsernames = document.getElementById('reviewer_usernames');
        const assigneeUsernames = document.getElementById('assignee_usernames');

        const formData = {
            source_branch: sourceBranch ? sourceBranch['value'] : '',
            target_branch: targetBranch ? targetBranch['value'] : '',
            start_with: startWith ? startWith['value'] : '',
            reviewer_usernames: reviewerUsernames ? reviewerUsernames['value'] : '',
            assignee_usernames: assigneeUsernames ? assigneeUsernames['value'] : '',
            last_saved: new Date().toISOString()
        };
        localStorage.setItem('gitlabMergeFormData', JSON.stringify(formData));
    } catch (error) {
        console.error('❌ 保存到localStorage失败:', error);
    }
}

/**
 * 清除本地存储的表单数据
 */
function clearLocalStorage() {
    try {
        localStorage.removeItem('gitlabMergeFormData');

        // 清空表单
        const form = document.getElementById('merge-form');
        if (form && form instanceof HTMLFormElement && typeof form.reset === 'function') {
            form.reset();
        }

        // 隐藏提示
        const storageNotice = document.getElementById('storage-notice');
        if (storageNotice) {
            storageNotice.style.display = 'none';
        }
    } catch (error) {
        console.error('❌ 清除localStorage失败:', error);
    }
}

/**
 * 表单提交处理函数
 */
function handleFormSubmit() {
    // 显示Loading动画
    showLoading();

    // 保存表单数据到localStorage
    saveFormData();
}

/**
 * 离开页面前先将Loading动画隐藏掉
 */
function handleBeforeLeave() {
    // 保存表单数据到localStorage
    saveFormData();
}

/**
 * 显示Loading动画
 */
function showLoading() {
    // 禁用提交按钮防止重复点击
    const submitButton = document.getElementById('merge-submit-btn');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.classList.add('btn-loading');
    }

    const loadingOverlay = document.getElementById('loading-overlay');
    const body = document.body;

    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        body.classList.add('loading-disabled');

        // 添加淡入动画
        setTimeout(() => {
            loadingOverlay.style.opacity = '1';
        }, 10);
    }
}

/**
 * 隐藏Loading动画
 */
function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    const body = document.body;
    const submitButton = document.getElementById('merge-submit-btn');

    if (loadingOverlay) {
        loadingOverlay.style.opacity = '0';

        setTimeout(() => {
            loadingOverlay.style.display = 'none';
            body.classList.remove('loading-disabled');

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.classList.remove('btn-loading');
            }
        }, 300);
    }
}

// 高级选项功能
function setupAdvancedOptions() {
    const toggleButton = document.getElementById('toggle-advanced');
    const advancedContent = document.getElementById('advanced-content');
    const refreshButton = document.getElementById('refresh-projects');
    const selectAllCheckbox = document.getElementById('select-all-projects');
    const projectList = document.getElementById('project-list');

    if (!toggleButton || !advancedContent) {
        return;
    }

    // 切换高级选项显示
    toggleButton.addEventListener('click', function () {
        const isHidden = advancedContent.style.display === 'none';
        advancedContent.style.display = isHidden ? 'block' : 'none';
        toggleButton.textContent = isHidden ? '🔼 收起选项' : '🔽 高级选项';

        // 如果是第一次展开，加载项目列表
        if (isHidden && projectList.children.length <= 1) {
            loadProjectList();
        }
    });

    // 刷新项目列表
    if (refreshButton) {
        refreshButton.addEventListener('click', loadProjectList);
    }

    // 全选/取消全选
    if (selectAllCheckbox && selectAllCheckbox instanceof HTMLInputElement) {
        selectAllCheckbox.addEventListener('change', function () {
            const checkboxes = projectList.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
            updateSpecificProjects();
        });
    }
}

// 加载项目列表
function loadProjectList() {
    const projectList = document.getElementById('project-list');
    if (!projectList) return;

    // 显示加载状态
    projectList.innerHTML = '<div class="loading-projects">加载中...</div>';

    // 发送请求获取项目列表
    fetch('/get_project_name_list', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.projects && data.projects.length > 0) {
                renderProjectList(data.projects);
            } else {
                projectList.innerHTML = '<div class="loading-projects">暂无项目</div>';
            }
        })
        .catch(error => {
            console.error('加载项目列表失败:', error);
            projectList.innerHTML = '<div class="loading-projects">加载失败</div>';
        });
}

// 渲染项目列表
function renderProjectList(projects) {
    const projectList = document.getElementById('project-list');
    if (!projectList) {
        return;
    }

    let html = '';
    projects.forEach(project => {
        html += `
            <div class="project-item">
                <input type="checkbox" id="project_${project}" name="project" value="${project}">
                <label for="project_${project}">${project}</label>
            </div>
        `;
    });

    projectList.innerHTML = html;

    // 为每个checkbox添加事件监听器
    const checkboxes = projectList.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSpecificProjects);
    });
}

// 更新特定项目隐藏字段
function updateSpecificProjects() {
    const checkboxes = document.querySelectorAll('#project-list input[type="checkbox"]:checked');
    const projectNames = Array.from(checkboxes).map(cb => cb['value'] || '');
    const specificProjectsInput = document.getElementById('specific_projects');

    if (specificProjectsInput) {
        specificProjectsInput.value = projectNames.join(',');
    }

    // 更新全选checkbox状态
    const selectAllCheckbox = document.getElementById('select-all-projects');
    const allCheckboxes = document.querySelectorAll('#project-list input[type="checkbox"]');
    if (selectAllCheckbox && allCheckboxes.length > 0) {
        selectAllCheckbox.checked = checkboxes.length === allCheckboxes.length && allCheckboxes.length > 0;
    }
}