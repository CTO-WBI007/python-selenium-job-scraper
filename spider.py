# main.py - 主程序入口
if __name__ == "__main__":
    import sys
    
    # 测试模式：快速调试选择器
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🔍 测试模式：只抓取第一页，开启详细日志")
        config = SpiderConfig(
            keywords=["Python"],
            max_pages=1,
            items_per_page=5,  # 只抓5条
            headless=False,
            save_html=True,    # 保存HTML用于分析
            save_csv=True,
            save_json=False,
            min_delay=2.0,
            max_delay=3.0
        )
    else:
        # 正常模式
        config = SpiderConfig(
            keywords=["Python"],  # 可以搜索多个关键词: ["Python", "数据分析", "Java"]
            max_pages=3,          # 每个关键词抓取 3 页
            items_per_page=30,
            headless=False,       # 显示浏览器窗口
            min_delay=3.0,
            max_delay=6.0,
            save_csv=True,
            save_json=True,
            save_html=False       # 不保存页面源码（文件太大）
        )
    
    # 创建爬虫实例
    spider = BossSpider(config)
    
    # 运行
    spider.run()


# ============ 独立的选择器调试工具 ============
"""
使用方法：
python boss_spider.py debug

这会打开浏览器并打印出所有可能的选择器，帮助你找到正确的 class 名称
"""

def debug_selectors():
    """调试模式：帮助找到正确的选择器"""
    print("\n" + "="*60)
    print("🔧 选择器调试工具")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        )
        page = browser.new_page()
        
        print("\n1. 访问 Boss 直聘...")
        page.goto("https://www.zhipin.com")
        time.sleep(5)
        # config.py - 配置文件
import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SpiderConfig:
    """爬虫配置"""
    # 浏览器配置
    chrome_path: str = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    headless: bool = False
    viewport: Dict = None
    
    # 搜索配置
    keywords: List[str] = None
    city: str = "全国"
    salary_range: str = ""  # 例如: "20-50"
    experience: str = ""  # 经验要求
    max_pages: int = 3
    items_per_page: int = 30
    
    # 反爬虫配置
    min_delay: float = 2.0
    max_delay: float = 5.0
    mouse_move_enabled: bool = True
    max_retries: int = 3
    
    # 数据存储
    output_dir: str = "data"
    save_html: bool = True
    save_csv: bool = True
    save_json: bool = True
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {'width': 1920, 'height': 1080}
        if self.keywords is None:
            self.keywords = ["Python"]
        os.makedirs(self.output_dir, exist_ok=True)


# selectors.py - 选择器配置
class Selectors:
    """统一管理所有选择器（防止页面改版后难以维护）"""
    
    # 搜索相关
    SEARCH_BOX = [".ipt-search", "input[name='query']", "#search-input"]
    SEARCH_BUTTON = [".btn-search", "button[type='submit']", ".search-btn"]
    
    # 弹窗关闭
    CLOSE_BUTTONS = [".btn-close", ".dialog-close", ".close-btn", "[class*='close']"]
    
    # 职位列表
    JOB_LIST = [".job-list", ".job-list-box", "[class*='job-list']"]
    JOB_CARD = [".job-card-wrapper", ".job-card", ".job-primary", "[class*='job-card']"]
    
    # 职位详情
    JOB_TITLE = [".job-title", ".job-name", "a.job-name", ".info-primary h3", "span.job-name"]
    JOB_LINK = ["a", ".job-card-left a"]
    SALARY = [".salary", ".red", "[class*='salary']", ".job-limit .red", "span.salary"]
    COMPANY_NAME = [".company-name", ".name", "h3.name", ".company-text h3", "span.company-name"]
    
    # 标签信息
    TAG_LIST = [".tag-list", ".job-tags", ".info-labels"]
    EXPERIENCE = [".tag-list li:first-child", "[class*='experience']"]
    EDUCATION = [".tag-list li:nth-child(2)", "[class*='education']"]
    LOCATION = [".job-area", ".area", "[class*='location']"]
    
    # 福利待遇
    WELFARE = [".info-desc", ".tag-list", "[class*='welfare']"]
    
    # 公司信息
    COMPANY_INFO = [".company-tag-list", ".company-info", ".info-company"]
    
    # 分页
    NEXT_PAGE = [".next", ".page-next", "[class*='next']"]
    PAGE_NUMBER = [".page-number", ".cur", ".active"]


# utils.py - 工具函数
import time
import random
import re
import json
from datetime import datetime
from typing import Optional, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Utils:
    """工具类"""
    
    @staticmethod
    def random_sleep(min_sec: float = 1, max_sec: float = 3):
        """随机延迟"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    @staticmethod
    def human_mouse_move(page):
        """模拟人类鼠标移动"""
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 1200)
            y = random.randint(100, 800)
            page.mouse.move(x, y, steps=random.randint(5, 15))
            time.sleep(random.uniform(0.1, 0.3))
    
    @staticmethod
    def validate_salary(salary: str) -> bool:
        """验证薪资格式"""
        if not salary or salary == "面议":
            return True
        # 匹配格式: "10-20K", "10K-20K", "1-2万", 或者包含数字
        # 放宽验证：只要包含数字或K就认为有效
        return bool(re.search(r'\d+', salary)) or 'K' in salary.upper()
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def parse_salary(salary: str) -> Dict:
        """解析薪资范围"""
        if not salary or salary == "面议":
            return {"min": 0, "max": 0, "unit": "面议"}
        
        # 提取数字
        numbers = re.findall(r'\d+', salary)
        
        if len(numbers) >= 2:
            min_val = int(numbers[0])
            max_val = int(numbers[1])
            
            # 判断单位
            if 'K' in salary.upper():
                unit = "K"
            elif '万' in salary:
                unit = "万"
                min_val *= 10
                max_val *= 10
            else:
                unit = "K"
            
            return {"min": min_val, "max": max_val, "unit": unit, "avg": (min_val + max_val) / 2}
        elif len(numbers) == 1:
            # 只有一个数字的情况，比如 "15K"
            val = int(numbers[0])
            if 'K' in salary.upper():
                unit = "K"
            elif '万' in salary:
                unit = "万"
                val *= 10
            else:
                unit = "K"
            return {"min": val, "max": val, "unit": unit, "avg": val}
        
        # 无法解析，但保留原始字符串
        return {"min": 0, "max": 0, "unit": "未知", "raw": salary}
    
    @staticmethod
    def save_to_json(data: List[Dict], filename: str):
        """保存为 JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 JSON: {filename}")
    
    @staticmethod
    def save_to_csv(data: List[Dict], filename: str):
        """保存为 CSV"""
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        logger.info(f"已保存 CSV: {filename}")


# parser.py - 数据解析器
class JobParser:
    """职位信息解析器"""
    
    @staticmethod
    def safe_get_text(element, selectors: List[str], default: str = "") -> str:
        """安全获取文本（尝试多个选择器）"""
        for selector in selectors:
            try:
                elem = element.query_selector(selector)
                if elem:
                    text = elem.inner_text().strip()
                    if text:
                        return Utils.clean_text(text)
            except Exception as e:
                continue
        return default
    
    @staticmethod
    def safe_get_attribute(element, selectors: List[str], attr: str, default: str = "") -> str:
        """安全获取属性"""
        for selector in selectors:
            try:
                elem = element.query_selector(selector)
                if elem:
                    value = elem.get_attribute(attr)
                    if value:
                        return value
            except:
                continue
        return default
    
    @classmethod
    def parse_job_card(cls, card, debug=False) -> Optional[Dict]:
        """解析单个职位卡片"""
        try:
            # 调试模式：打印卡片HTML
            if debug:
                logger.debug(f"Card HTML: {card.inner_html()[:500]}")
            
            # 基础信息
            title = cls.safe_get_text(card, Selectors.JOB_TITLE, "未知职位")
            link = cls.safe_get_attribute(card, Selectors.JOB_LINK, "href", "")
            if link and not link.startswith("http"):
                link = f"https://www.zhipin.com{link}"
            
            company = cls.safe_get_text(card, Selectors.COMPANY_NAME, "未知公司")
            salary = cls.safe_get_text(card, Selectors.SALARY, "面议")
            
            # 如果没抓到薪资，尝试从整个卡片文本中提取
            if salary == "面议" or not salary:
                card_text = card.inner_text()
                # 尝试匹配薪资模式
                salary_match = re.search(r'(\d+[-~]\d+K|\d+K[-~]\d+K|\d+[-~]\d+万)', card_text)
                if salary_match:
                    salary = salary_match.group(1)
            
            # 标签信息
            experience = cls.safe_get_text(card, Selectors.EXPERIENCE)
            education = cls.safe_get_text(card, Selectors.EDUCATION)
            location = cls.safe_get_text(card, Selectors.LOCATION)
            
            # 福利待遇
            welfare = cls.safe_get_text(card, Selectors.WELFARE)
            
            # 公司信息
            company_info = cls.safe_get_text(card, Selectors.COMPANY_INFO)
            
            # 解析薪资
            salary_parsed = Utils.parse_salary(salary)
            
            job_data = {
                "职位名称": title,
                "公司名称": company,
                "薪资": salary,
                "薪资最低": salary_parsed.get("min", 0),
                "薪资最高": salary_parsed.get("max", 0),
                "薪资平均": salary_parsed.get("avg", 0),
                "经验要求": experience,
                "学历要求": education,
                "工作地点": location,
                "福利待遇": welfare,
                "公司信息": company_info,
                "职位链接": link,
                "抓取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 数据验证
            if cls.validate_job_data(job_data):
                return job_data
            else:
                logger.warning(f"数据验证失败: {title} | 薪资: {salary}")
                if debug:
                    logger.debug(f"Job data: {job_data}")
                return None
                
        except Exception as e:
            logger.error(f"解析职位卡片失败: {e}")
            return None
    
    @staticmethod
    def validate_job_data(job: Dict) -> bool:
        """验证职位数据完整性"""
        required_fields = ["职位名称", "公司名称"]
        
        # 检查必填字段
        for field in required_fields:
            if not job.get(field) or job[field] in ["未知职位", "未知公司", ""]:
                return False
        
        # 放宽薪资验证：只要不是空的就行
        if not job.get("薪资"):
            return False
        
        return True


# spider.py - 主爬虫类
from playwright.sync_api import sync_playwright, Page, Browser
from typing import List, Dict

class BossSpider:
    """Boss 直聘爬虫主类"""
    
    def __init__(self, config: SpiderConfig = None):
        self.config = config or SpiderConfig()
        self.jobs: List[Dict] = []
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.stats = {
            "total_crawled": 0,
            "total_valid": 0,
            "total_failed": 0,
            "start_time": None,
            "end_time": None
        }
    
    def setup_browser(self, playwright):
        """初始化浏览器"""
        logger.info("正在启动 Chrome 浏览器...")
        
        self.browser = playwright.chromium.launch(
            headless=self.config.headless,
            executable_path=self.config.chrome_path,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = self.browser.new_context(
            viewport=self.config.viewport,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            permissions=[]
        )
        
        self.page = context.new_page()
        
        # 注入反检测脚本
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
            window.chrome = {
                runtime: {},
                app: {},
                csi: function() {},
                loadTimes: function() {}
            };
        """)
        
        logger.info("浏览器启动成功")
    
    def close_popups(self):
        """关闭可能出现的弹窗"""
        for selector in Selectors.CLOSE_BUTTONS:
            try:
                self.page.click(selector, timeout=2000)
                logger.info("已关闭弹窗")
                Utils.random_sleep(0.5, 1)
            except:
                continue
    
    def search_jobs(self, keyword: str, first_search: bool = True):
        """搜索职位"""
        logger.info(f"正在搜索关键词: {keyword}")
        
        # 如果不是第一次搜索，先回到首页
        if not first_search:
            logger.info("返回首页重新搜索...")
            self.page.goto("https://www.zhipin.com", timeout=30000)
            Utils.random_sleep(3, 5)
            self.close_popups()
        
        # 尝试多个搜索框选择器
        search_box = None
        for selector in Selectors.SEARCH_BOX:
            try:
                search_box = self.page.wait_for_selector(selector, timeout=10000)
                if search_box:
                    logger.info(f"使用选择器 '{selector}' 找到搜索框")
                    break
            except:
                continue
        
        if not search_box:
            # 保存页面用于调试
            with open(f"{self.config.output_dir}/debug_search_page.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            raise Exception("未找到搜索框，已保存页面到 debug_search_page.html")
        
        # 清空并输入关键词
        search_box.click()
        Utils.random_sleep(0.5, 1)
        
        # 清空输入框 - 使用多种方法
        search_box.fill("")
        self.page.keyboard.press("Control+A")
        self.page.keyboard.press("Backspace")
        Utils.random_sleep(0.3, 0.6)
        
        # 模拟逐字输入
        for char in keyword:
            search_box.type(char, delay=random.randint(50, 150))
        
        Utils.random_sleep(1, 2)
        
        # 点击搜索按钮
        for selector in Selectors.SEARCH_BUTTON:
            try:
                self.page.click(selector, timeout=5000)
                logger.info("已点击搜索按钮")
                break
            except:
                continue
        
        # 等待结果加载
        Utils.random_sleep(5, 8)
        
        try:
            self.page.wait_for_selector(Selectors.JOB_LIST[0], timeout=15000)
            logger.info("职位列表加载完成")
        except:
            logger.warning("等待职位列表超时，尝试继续...")
    
    def crawl_current_page(self, debug=False) -> int:
        """抓取当前页面的职位"""
        # 保存页面源码（用于调试）
        if self.config.save_html or debug:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = f"{self.config.output_dir}/page_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(self.page.content())
            logger.info(f"已保存页面源码: {html_file}")
        
        # 查找职位卡片
        job_cards = []
        for selector in Selectors.JOB_CARD:
            try:
                job_cards = self.page.query_selector_all(selector)
                if job_cards:
                    logger.info(f"使用选择器 '{selector}' 找到 {len(job_cards)} 个职位")
                    break
            except:
                continue
        
        if not job_cards:
            logger.warning("未找到任何职位卡片")
            # 如果第一次失败，开启调试模式保存前几个元素
            if debug:
                with open(f"{self.config.output_dir}/debug_elements.txt", "w", encoding="utf-8") as f:
                    f.write("Page title: " + self.page.title() + "\n\n")
                    f.write("Page URL: " + self.page.url + "\n\n")
            return 0
        
        count = 0
        for i, card in enumerate(job_cards[:self.config.items_per_page], 1):
            self.stats["total_crawled"] += 1
            
            # 前3个卡片开启调试
            job_data = JobParser.parse_job_card(card, debug=(i <= 3 and debug))
            if job_data:
                self.jobs.append(job_data)
                self.stats["total_valid"] += 1
                count += 1
                logger.info(f"[{i}/{len(job_cards)}] ✓ {job_data['职位名称']} @ {job_data['公司名称']} - {job_data['薪资']}")
            else:
                self.stats["total_failed"] += 1
                logger.warning(f"[{i}/{len(job_cards)}] ✗ 解析失败")
        
        return count
    
    def go_to_next_page(self) -> bool:
        """翻到下一页"""
        try:
            # 滚动到底部
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            Utils.random_sleep(1, 2)
            
            # 查找下一页按钮
            for selector in Selectors.NEXT_PAGE:
                try:
                    next_btn = self.page.query_selector(selector)
                    if next_btn and next_btn.is_visible():
                        # 检查是否可点击
                        if "disabled" in (next_btn.get_attribute("class") or ""):
                            logger.info("已到最后一页")
                            return False
                        
                        next_btn.click()
                        logger.info("已点击下一页")
                        Utils.random_sleep(5, 8)
                        return True
                except:
                    continue
            
            logger.warning("未找到下一页按钮")
            return False
            
        except Exception as e:
            logger.error(f"翻页失败: {e}")
            return False
    
    def run(self):
        """运行爬虫"""
        self.stats["start_time"] = datetime.now()
        logger.info("=" * 60)
        logger.info("Boss 直聘爬虫启动")
        logger.info(f"搜索关键词: {', '.join(self.config.keywords)}")
        logger.info(f"最大页数: {self.config.max_pages}")
        logger.info("=" * 60)
        
        with sync_playwright() as playwright:
            try:
                self.setup_browser(playwright)
                
                # 打开 Boss 直聘
                logger.info("正在访问 Boss 直聘...")
                self.page.goto("https://www.zhipin.com", timeout=30000)
                Utils.random_sleep(3, 5)
                
                # 模拟人类行为
                if self.config.mouse_move_enabled:
                    Utils.human_mouse_move(self.page)
                
                # 关闭弹窗
                self.close_popups()
                
                # 遍历关键词
                for idx, keyword in enumerate(self.config.keywords):
                    # 搜索
                    self.search_jobs(keyword, first_search=(idx == 0))
                    
                    # 抓取多页
                    for page_num in range(1, self.config.max_pages + 1):
                        logger.info(f"\n{'='*50}")
                        logger.info(f"关键词: {keyword} - 第 {page_num} 页")
                        logger.info(f"{'='*50}")
                        
                        # 第一页第一个关键词开启调试
                        debug_mode = (idx == 0 and page_num == 1)
                        count = self.crawl_current_page(debug=debug_mode)
                        logger.info(f"本页抓取: {count} 条有效数据")
                        
                        # 如果不是最后一页，翻页
                        if page_num < self.config.max_pages:
                            if not self.go_to_next_page():
                                logger.info("无法继续翻页，停止抓取")
                                break
                        
                        # 随机延迟
                        Utils.random_sleep(self.config.min_delay, self.config.max_delay)
                
                # 保存数据
                self.save_results()
                
            except Exception as e:
                logger.error(f"爬虫运行出错: {e}", exc_info=True)
            finally:
                self.stats["end_time"] = datetime.now()
                self.print_stats()
                
                input("\n按 Enter 关闭浏览器...")
                if self.browser:
                    self.browser.close()
    
    def save_results(self):
        """保存结果"""
        if not self.jobs:
            logger.warning("没有抓取到任何数据")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存 CSV
        if self.config.save_csv:
            csv_file = f"{self.config.output_dir}/boss_jobs_{timestamp}.csv"
            Utils.save_to_csv(self.jobs, csv_file)
        
        # 保存 JSON
        if self.config.save_json:
            json_file = f"{self.config.output_dir}/boss_jobs_{timestamp}.json"
            Utils.save_to_json(self.jobs, json_file)
        
        logger.info(f"\n✅ 数据保存完成！共 {len(self.jobs)} 条")
    
    def print_stats(self):
        """打印统计信息"""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 爬取统计")
        logger.info("=" * 60)
        logger.info(f"总共抓取: {self.stats['total_crawled']} 条")
        logger.info(f"有效数据: {self.stats['total_valid']} 条")
        logger.info(f"失败数据: {self.stats['total_failed']} 条")
        logger.info(f"成功率: {self.stats['total_valid']/max(self.stats['total_crawled'],1)*100:.1f}%")
        logger.info(f"耗时: {duration:.1f} 秒")
        logger.info("=" * 60)


# main.py - 主程序入口
if __name__ == "__main__":
    import sys
    
    # 测试模式：快速调试选择器
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("🔍 测试模式：只抓取第一页，开启详细日志")
        config = SpiderConfig(
            keywords=["Python"],
            max_pages=1,
            items_per_page=5,  # 只抓5条
            headless=False,
            save_html=True,    # 保存HTML用于分析
            save_csv=True,
            save_json=False,
            min_delay=2.0,
            max_delay=3.0
        )
    else:
        # 正常模式
        config = SpiderConfig(
            keywords=["Python"],  # 可以搜索多个关键词: ["Python", "数据分析", "Java"]
            max_pages=3,          # 每个关键词抓取 3 页
            items_per_page=30,
            headless=False,       # 显示浏览器窗口
            min_delay=3.0,
            max_delay=6.0,
            save_csv=True,
            save_json=True,
            save_html=False       # 不保存页面源码（文件太大）
        )
    
    # 创建爬虫实例
    spider = BossSpider(config)
    
    # 运行
    spider.run()