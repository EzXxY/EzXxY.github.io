#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML目录自动添加工具
自动检测HTML文件结构并添加智能目录功能

使用方法:
python toc_injector.py input.html [output.html]

如果不指定输出文件，将在原文件名后添加_with_toc后缀
"""

import os
import re
import sys
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import codecs

class TocInjector:
    def __init__(self):
        self.toc_css = '''
/* 目录样式 - Github风格设计 */
.mdtht-toc {
    position: fixed;
    top: 80px;
    right: 24px;
    width: 300px;
    max-height: calc(100vh - 160px);
    background: #ffffff;
    border: 1px solid #d1d9e0;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(140, 149, 159, 0.2);
    z-index: 1000;
    overflow: hidden;
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    transform: translateX(0);
    opacity: 1;
    visibility: visible;
}

/* 隐藏状态 */
.mdtht-toc.hidden {
    transform: translateX(calc(100% + 24px));
    opacity: 0;
    visibility: hidden;
}

/* 小屏幕自动隐藏 */
@media (max-width: 1200px) {
    .mdtht-toc {
        transform: translateX(calc(100% + 24px));
        opacity: 0;
        visibility: hidden;
    }

    .mdtht-toc.show {
        transform: translateX(0);
        opacity: 1;
        visibility: visible;
    }
}

/* 移动端适配 */
@media (max-width: 768px) {
    .mdtht-toc {
        top: 20px;
        right: 20px;
        left: 20px;
        width: calc(100vw - 40px);
        max-height: calc(100vh - 40px);
        border-radius: 8px;
        transform: translateY(-110%);
    }

    .mdtht-toc.show {
        transform: translateY(0);
    }
}

.mdtht-toc-header {
    padding: 16px 20px 12px;
    background: linear-gradient(135deg, #f6f8fa 0%, #ffffff 100%);
    border-bottom: 1px solid #e1e8ed;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 10;
}

.mdtht-toc-title {
    font-size: 14px;
    font-weight: 600;
    color: #24292f;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.mdtht-toc-title::before {
    content: "📑";
    font-size: 16px;
}

.mdtht-toc-content {
    max-height: calc(100vh - 240px);
    overflow-y: auto;
    padding: 8px 0 16px;
    scrollbar-width: thin;
    scrollbar-color: #d1d9e0 transparent;
}

.mdtht-toc-content::-webkit-scrollbar {
    width: 6px;
}

.mdtht-toc-content::-webkit-scrollbar-track {
    background: transparent;
}

.mdtht-toc-content::-webkit-scrollbar-thumb {
    background: #d1d9e0;
    border-radius: 3px;
}

.mdtht-toc-content::-webkit-scrollbar-thumb:hover {
    background: #8c959f;
}

.mdtht-toc-list {
    list-style: none;
    margin: 0;
    padding: 0;
}

.mdtht-toc-item {
    margin: 0;
    position: relative;
}

.mdtht-toc-link {
    display: block;
    padding: 6px 20px 6px 16px;
    color: #656d76;
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.2s ease;
    line-height: 1.4;
    position: relative;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.mdtht-toc-link:hover {
    color: #0969da;
    background: rgba(9, 105, 218, 0.05);
    border-left-color: rgba(9, 105, 218, 0.3);
}

.mdtht-toc-link.active {
    color: #0969da;
    background: rgba(9, 105, 218, 0.1);
    border-left-color: #0969da;
    font-weight: 500;
}

/* 标题层级样式 */
.mdtht-toc-h1 .mdtht-toc-link {
    padding-left: 16px;
    font-weight: 600;
    font-size: 13px;
    color: #24292f;
}

.mdtht-toc-h2 .mdtht-toc-link {
    padding-left: 28px;
    font-size: 12px;
}

.mdtht-toc-h3 .mdtht-toc-link {
    padding-left: 40px;
    font-size: 12px;
    color: #7c8b96;
}

.mdtht-toc-h4 .mdtht-toc-link {
    padding-left: 52px;
    font-size: 11px;
    color: #7c8b96;
}

.mdtht-toc-h5 .mdtht-toc-link {
    padding-left: 64px;
    font-size: 11px;
    color: #8c959f;
}

.mdtht-toc-h6 .mdtht-toc-link {
    padding-left: 76px;
    font-size: 11px;
    color: #8c959f;
}

/* 切换按钮 - 仅在需要时显示 */
.mdtht-toc-toggle {
    position: fixed;
    top: 90px;
    right: 24px;
    width: 48px;
    height: 48px;
    background: #ffffff;
    border: 1px solid #d1d9e0;
    border-radius: 24px;
    color: #656d76;
    cursor: pointer;
    z-index: 1001;
    display: none;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 12px rgba(140, 149, 159, 0.15);
    transition: all 0.2s ease;
}

.mdtht-toc-toggle:hover {
    background: #f6f8fa;
    border-color: #8c959f;
    color: #24292f;
    transform: scale(1.05);
}

/* 小屏幕时显示切换按钮 */
@media (max-width: 1200px) {
    .mdtht-toc-toggle {
        display: flex;
    }
}

.mdtht-toc-close {
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    color: #656d76;
    padding: 6px;
    border-radius: 6px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
}

.mdtht-toc-close:hover {
    background: rgba(175, 184, 193, 0.2);
    color: #24292f;
}

/* 目录计数显示 */
.mdtht-toc-count {
    font-size: 11px;
    color: #8c959f;
    background: #f6f8fa;
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 4px;
}

/* 滚动进度条 */
.mdtht-toc-progress {
    position: absolute;
    left: 0;
    top: 0;
    width: 3px;
    height: 0%;
    background: linear-gradient(180deg, #0969da 0%, #218bff 100%);
    transition: height 0.1s ease;
    border-radius: 0 2px 2px 0;
}
'''

        self.toc_html = '''
<!-- 目录切换按钮 -->
<button class="mdtht-toc-toggle" title="显示目录">📑</button>

<!-- 目录容器 -->
<div class="mdtht-toc" id="mdtht-toc">
    <div class="mdtht-toc-header">
        <h3 class="mdtht-toc-title">
            目录
            <span class="mdtht-toc-count">0</span>
        </h3>
        <button class="mdtht-toc-close" title="隐藏目录">✕</button>
    </div>
    <div class="mdtht-toc-content">
        <ul class="mdtht-toc-list" id="mdtht-toc-list">
            <!-- 目录项将通过JavaScript动态生成 -->
        </ul>
    </div>
</div>
'''

        self.toc_js = '''
<script>
class MdTht {
    constructor() {
        this.toc = document.getElementById('mdtht-toc');
        this.tocList = document.getElementById('mdtht-toc-list');
        this.toggle = document.querySelector('.mdtht-toc-toggle');
        this.headings = [];
        this.activeId = null;
        this.isVisible = true;

        this.init();
    }

    init() {
        this.generateToc();
        this.bindEvents();
        this.checkScreenSize();
        this.updateProgress();

        // 监听屏幕尺寸变化
        window.addEventListener('resize', () => this.checkScreenSize());
        window.addEventListener('scroll', () => this.updateProgress());
    }

    generateToc() {
        const headingSelectors = 'h1, h2, h3, h4, h5, h6';
        const headingElements = document.querySelectorAll(headingSelectors);

        this.headings = Array.from(headingElements)
            .filter(heading => {
                // 排除目录容器内的标题
                return !heading.closest('.mdtht-toc');
            })
            .map((heading, index) => {
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }

                return {
                    element: heading,
                    id: heading.id,
                    text: heading.textContent.trim(),
                    level: parseInt(heading.tagName.charAt(1))
                };
            });

        this.renderToc();
    }

    renderToc() {
        this.tocList.innerHTML = '';

        // 添加进度条
        const progress = document.createElement('div');
        progress.className = 'mdtht-toc-progress';
        this.toc.appendChild(progress);

        this.headings.forEach(heading => {
            const li = document.createElement('li');
            li.className = `mdtht-toc-item mdtht-toc-h${heading.level}`;

            const a = document.createElement('a');
            a.className = 'mdtht-toc-link';
            a.href = `#${heading.id}`;
            a.textContent = heading.text;
            a.dataset.target = heading.id;
            a.title = heading.text;

            li.appendChild(a);
            this.tocList.appendChild(li);
        });

        // 更新标题中的计数
        const countElement = document.querySelector('.mdtht-toc-count');
        if (countElement) {
            countElement.textContent = this.headings.length;
        }
    }

    bindEvents() {
        let ticking = false;

        // 滚动事件
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.updateActiveHeading();
                    ticking = false;
                });
                ticking = true;
            }
        });

        // 目录项点击事件
        this.tocList.addEventListener('click', (e) => {
            if (e.target.classList.contains('mdtht-toc-link')) {
                e.preventDefault();
                const targetId = e.target.dataset.target;
                const targetElement = document.getElementById(targetId);

                if (targetElement) {
                    const offset = 80;
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - offset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });

        // 切换按钮事件
        if (this.toggle) {
            this.toggle.addEventListener('click', () => this.toggleToc());
        }

        // 关闭按钮事件
        const closeBtn = document.querySelector('.mdtht-toc-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.toggleToc());
        }
    }

    checkScreenSize() {
        const isLargeScreen = window.innerWidth > 1200;

        if (isLargeScreen) {
            this.toc.classList.remove('hidden');
            this.toggle.style.display = 'none';
            this.isVisible = true;
        } else {
            this.toc.classList.add('hidden');
            this.toc.classList.remove('show');
            this.toggle.style.display = 'flex';
            this.isVisible = false;
        }
    }

    toggleToc() {
        const isLargeScreen = window.innerWidth > 1200;

        if (isLargeScreen) {
            this.toc.classList.toggle('hidden');
            this.isVisible = !this.toc.classList.contains('hidden');

            if (this.isVisible) {
                this.toggle.style.display = 'none';
            } else {
                this.toggle.style.display = 'flex';
            }
        } else {
            this.toc.classList.toggle('show');
            this.isVisible = this.toc.classList.contains('show');
        }
    }

    updateActiveHeading() {
        let activeHeading = null;

        for (let i = this.headings.length - 1; i >= 0; i--) {
            const heading = this.headings[i];
            const rect = heading.element.getBoundingClientRect();

            if (rect.top <= 100) {
                activeHeading = heading;
                break;
            }
        }

        if (activeHeading && activeHeading.id !== this.activeId) {
            const prevActive = this.tocList.querySelector('.mdtht-toc-link.active');
            if (prevActive) {
                prevActive.classList.remove('active');
            }

            const newActive = this.tocList.querySelector(`[data-target="${activeHeading.id}"]`);
            if (newActive) {
                newActive.classList.add('active');
                this.activeId = activeHeading.id;
                this.scrollIntoView(newActive);
            }
        }
    }

    updateProgress() {
        const progress = document.querySelector('.mdtht-toc-progress');
        if (!progress) return;

        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight - windowHeight;
        const scrolled = window.pageYOffset;
        const progressPercentage = (scrolled / documentHeight) * 100;

        progress.style.height = Math.min(100, Math.max(0, progressPercentage)) + '%';
    }

    scrollIntoView(element) {
        const container = this.toc.querySelector('.mdtht-toc-content');
        const containerRect = container.getBoundingClientRect();
        const elementRect = element.getBoundingClientRect();

        if (elementRect.top < containerRect.top || elementRect.bottom > containerRect.bottom) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    new MdTht();
});

// 页面外点击关闭（仅在小屏幕）
document.addEventListener('click', function(e) {
    if (window.innerWidth <= 1200) {
        const toc = document.getElementById('mdtht-toc');
        const toggle = document.querySelector('.mdtht-toc-toggle');

        if (toc && toggle && !toc.contains(e.target) && !toggle.contains(e.target)) {
            toc.classList.remove('show');
        }
    }
});
</script>
'''

    def detect_encoding(self, file_path):
        """检测文件编码"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'iso-8859-1']

        for encoding in encodings:
            try:
                with codecs.open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue

        return 'utf-8'  # 默认返回utf-8

    def read_html_file(self, file_path):
        """读取HTML文件"""
        encoding = self.detect_encoding(file_path)
        print(f"检测到文件编码: {encoding}")

        try:
            with codecs.open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except Exception as e:
            print(f"错误：无法读取文件 {file_path}: {e}")
            return None, None

    def check_existing_toc(self, content):
        """检查是否已存在目录功能"""
        markers = [
            'mdtht-toc',
            'class MdTht',
            '目录切换按钮',
            'mdtht-toc-toggle'
        ]

        for marker in markers:
            if marker in content:
                return True
        return False

    def inject_toc(self, content):
        """注入目录功能"""
        soup = BeautifulSoup(content, 'html.parser')

        # 检查基本HTML结构
        if not soup.find('html') or not soup.find('head') or not soup.find('body'):
            print("警告：HTML文件结构不完整，可能影响目录功能")

        # 统计标题数量
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        heading_count = len(headings)
        print(f"检测到 {heading_count} 个标题元素")

        if heading_count == 0:
            print("警告：未检测到任何标题元素(h1-h6)，目录将为空")

        # 1. 添加CSS到head中
        head = soup.find('head')
        if head:
            # 查找最后一个style标签
            last_style = head.find_all('style')
            if last_style:
                # 在最后一个style标签后添加
                new_style = soup.new_tag('style')
                new_style.string = self.toc_css
                last_style[-1].insert_after(new_style)
            else:
                # 如果没有style标签，直接添加到head末尾
                new_style = soup.new_tag('style')
                new_style.string = self.toc_css
                head.append(new_style)
            print("✓ CSS样式已添加")
        else:
            print("错误：未找到<head>标签，无法添加CSS")
            return None

        # 2. 添加HTML结构到body开始
        body = soup.find('body')
        if body:
            # 解析HTML结构并插入到body开始
            toc_soup = BeautifulSoup(self.toc_html, 'html.parser')
            for element in toc_soup.children:
                if element.name:  # 只插入标签元素
                    body.insert(0, element)
            print("✓ HTML结构已添加")
        else:
            print("错误：未找到<body>标签，无法添加HTML结构")
            return None

        # 3. 添加JavaScript到body结束前
        js_soup = BeautifulSoup(self.toc_js, 'html.parser')
        script_tag = js_soup.find('script')
        if script_tag:
            body.append(script_tag)
            print("✓ JavaScript功能已添加")

        return str(soup)

    def process_file(self, input_file, output_file=None):
        """处理单个文件"""
        input_path = Path(input_file)

        # 检查输入文件是否存在
        if not input_path.exists():
            print(f"错误：文件 {input_file} 不存在")
            return False

        # 确定输出文件路径
        if output_file is None:
            output_path = input_path.parent / f"{input_path.stem}_with_toc{input_path.suffix}"
        else:
            output_path = Path(output_file)

        print(f"处理文件: {input_file}")
        print(f"输出文件: {output_path}")

        # 读取文件
        content, encoding = self.read_html_file(input_file)
        if content is None:
            return False

        # 检查是否已存在目录
        if self.check_existing_toc(content):
            print("警告：检测到文件中可能已存在目录功能")
            response = input("是否继续添加？这可能导致重复功能 (y/N): ")
            if response.lower() != 'y':
                print("操作已取消")
                return False

        # 注入目录功能
        result = self.inject_toc(content)
        if result is None:
            print("错误：目录注入失败")
            return False

        # 写入输出文件
        try:
            with codecs.open(output_path, 'w', encoding=encoding) as f:
                f.write(result)
            print(f"✓ 目录功能已成功添加到: {output_path}")
            return True
        except Exception as e:
            print(f"错误：无法写入文件 {output_path}: {e}")
            return False

    def batch_process(self, directory, pattern="*.html"):
        """批量处理目录中的HTML文件"""
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"错误：目录 {directory} 不存在")
            return

        html_files = list(dir_path.glob(pattern))
        if not html_files:
            print(f"错误：在目录 {directory} 中未找到匹配 {pattern} 的文件")
            return

        print(f"找到 {len(html_files)} 个HTML文件")

        success_count = 0
        for html_file in html_files:
            print(f"\n{'='*50}")
            if self.process_file(str(html_file)):
                success_count += 1

        print(f"\n批量处理完成: {success_count}/{len(html_files)} 个文件处理成功")

def main():
    parser = argparse.ArgumentParser(
        description="HTML目录自动添加工具 - 为HTML文件添加智能目录功能",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python toc_injector.py input.html                    # 输出到 input_with_toc.html
  python toc_injector.py input.html output.html        # 指定输出文件
  python toc_injector.py --batch ./html_files/         # 批量处理目录中的所有HTML文件
  python toc_injector.py --batch ./docs/ --pattern "*.htm"  # 批量处理指定模式的文件
        """
    )

    parser.add_argument('input', nargs='?', help='输入HTML文件路径或目录路径（批量模式）')
    parser.add_argument('output', nargs='?', help='输出HTML文件路径（可选）')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    parser.add_argument('--pattern', default='*.html', help='批量处理时的文件匹配模式（默认: *.html）')

    args = parser.parse_args()

    # 检查参数
    if not args.input:
        parser.print_help()
        return

    injector = TocInjector()

    print("HTML目录自动添加工具")
    print("="*50)

    if args.batch:
        # 批量处理模式
        injector.batch_process(args.input, args.pattern)
    else:
        # 单文件处理模式
        injector.process_file(args.input, args.output)

    print("\n处理完成！")

if __name__ == "__main__":
    main()