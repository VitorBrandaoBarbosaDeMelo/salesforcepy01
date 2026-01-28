#!/usr/bin/env python3
"""
Salesforce Approval Automation Bot
===================================
Minimalist script for monitoring and automating approval requests in Salesforce.

This script:
1. Monitors Salesforce page for new external approval requests
2. Integrates with CSV data for decision making
3. Automates approval clicks in the manager panel
4. Runs in headless mode optimized for GitHub Codespaces
"""

import csv
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options


class SalesforceApprovalBot:
    """Automates Salesforce approval request processing."""
    
    def __init__(self, csv_file='approvals_data.csv', headless=True):
        """
        Initialize the bot with Chrome driver.
        
        Args:
            csv_file: Path to CSV file with approval rules
            headless: Run browser in headless mode
        """
        self.csv_file = csv_file
        self.approved_ids = set()
        self.approval_rules = self._load_approval_rules()
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless):
        """Configure Chrome driver for GitHub Codespaces."""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Optimized for Codespaces
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        return driver
    
    def _load_approval_rules(self):
        """Load approval rules from CSV file."""
        rules = {}
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    request_id = row.get('request_id', '').strip()
                    auto_approve = row.get('auto_approve', '').strip().lower() == 'true'
                    rules[request_id] = auto_approve
            print(f"✓ Loaded {len(rules)} approval rules from {self.csv_file}")
        except FileNotFoundError:
            print(f"⚠ Warning: {self.csv_file} not found. Using empty rules.")
        except Exception as e:
            print(f"⚠ Error loading CSV: {e}")
        return rules
    
    def connect_to_salesforce(self, url):
        """
        Connect to an already open Salesforce page.
        
        Args:
            url: Salesforce approval page URL
        """
        print(f"→ Connecting to Salesforce: {url}")
        self.driver.get(url)
        time.sleep(2)  # Allow page to load
        print("✓ Connected to Salesforce")
    
    def find_approval_requests(self):
        """
        Find pending approval requests on the page.
        
        Returns:
            List of approval request elements
        """
        try:
            # Common Salesforce approval request selectors
            # Adjust these based on your actual Salesforce page structure
            selectors = [
                "//div[contains(@class, 'approval-item')]",
                "//tr[contains(@class, 'approval-request')]",
                "//div[contains(@class, 'slds-card') and contains(., 'Approval')]",
                "//lightning-card[contains(@title, 'Approval')]",
            ]
            
            requests = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        requests.extend(elements)
                        print(f"✓ Found {len(elements)} approval requests using selector: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            return requests
        except Exception as e:
            print(f"⚠ Error finding approval requests: {e}")
            return []
    
    def extract_request_info(self, request_element):
        """
        Extract information from approval request element.
        
        Args:
            request_element: Selenium web element
            
        Returns:
            Dict with request_id and other metadata
        """
        try:
            # Try to find request ID in various ways
            request_id = None
            
            # Method 1: Look for ID in data attributes
            for attr in ['data-id', 'data-request-id', 'id']:
                try:
                    request_id = request_element.get_attribute(attr)
                    if request_id:
                        break
                except:
                    pass
            
            # Method 2: Look for ID in text content
            if not request_id:
                text = request_element.text
                # Extract ID patterns like "REQ-12345" or "AP-67890"
                import re
                match = re.search(r'(REQ|AP|AR)-?\d+', text, re.IGNORECASE)
                if match:
                    request_id = match.group(0)
            
            return {
                'request_id': request_id or 'UNKNOWN',
                'element': request_element,
                'text': request_element.text[:100]  # First 100 chars
            }
        except Exception as e:
            print(f"⚠ Error extracting request info: {e}")
            return None
    
    def should_approve(self, request_id):
        """
        Check if request should be auto-approved based on CSV rules.
        
        Args:
            request_id: The request ID
            
        Returns:
            Boolean indicating if request should be approved
        """
        # Check if already processed
        if request_id in self.approved_ids:
            return False
        
        # Check CSV rules
        return self.approval_rules.get(request_id, False)
    
    def approve_request(self, request_info):
        """
        Click approve button for a request.
        
        Args:
            request_info: Dict with request information
        """
        try:
            request_id = request_info['request_id']
            element = request_info['element']
            
            # Common approval button selectors
            approve_buttons = [
                ".//button[contains(., 'Approve') or contains(., 'Aprovar')]",
                ".//button[contains(@class, 'approve')]",
                ".//a[contains(@class, 'approve')]",
                ".//input[@type='button' and contains(@value, 'Approve')]",
            ]
            
            button_found = False
            for selector in approve_buttons:
                try:
                    approve_btn = element.find_element(By.XPATH, selector)
                    if approve_btn and approve_btn.is_displayed() and approve_btn.is_enabled():
                        approve_btn.click()
                        button_found = True
                        print(f"✓ Approved request: {request_id}")
                        self.approved_ids.add(request_id)
                        time.sleep(1)  # Wait after click
                        break
                except NoSuchElementException:
                    continue
            
            if not button_found:
                print(f"⚠ Approve button not found for: {request_id}")
                
        except Exception as e:
            print(f"✗ Error approving request: {e}")
    
    def monitor_and_approve(self, check_interval=10, max_iterations=None):
        """
        Main monitoring loop.
        
        Args:
            check_interval: Seconds between checks
            max_iterations: Max number of checks (None for infinite)
        """
        iteration = 0
        print(f"\n{'='*60}")
        print("Starting Salesforce Approval Monitor")
        print(f"{'='*60}")
        print(f"Check interval: {check_interval}s")
        print(f"Max iterations: {max_iterations or 'Infinite'}")
        print(f"{'='*60}\n")
        
        try:
            while True:
                iteration += 1
                print(f"\n[Iteration {iteration}] Checking for approval requests...")
                
                # Find approval requests
                requests = self.find_approval_requests()
                
                if not requests:
                    print("  No approval requests found")
                else:
                    print(f"  Found {len(requests)} approval request(s)")
                    
                    # Process each request
                    for idx, request in enumerate(requests, 1):
                        request_info = self.extract_request_info(request)
                        
                        if not request_info:
                            continue
                        
                        request_id = request_info['request_id']
                        print(f"\n  [{idx}] Request ID: {request_id}")
                        
                        if self.should_approve(request_id):
                            print(f"      ✓ Auto-approve enabled in CSV")
                            self.approve_request(request_info)
                        else:
                            print(f"      ⊘ Auto-approve not enabled or already processed")
                
                # Check if should continue
                if max_iterations and iteration >= max_iterations:
                    print(f"\n✓ Reached max iterations ({max_iterations})")
                    break
                
                # Wait before next check
                print(f"\n  Waiting {check_interval}s before next check...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⊗ Monitoring stopped by user")
        except Exception as e:
            print(f"\n✗ Error in monitoring loop: {e}")
            raise
    
    def close(self):
        """Clean up and close browser."""
        try:
            self.driver.quit()
            print("\n✓ Browser closed")
        except:
            pass


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Salesforce Approval Automation Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor with default settings
  python salesforce_approval_bot.py --url "https://your-salesforce.com/approvals"
  
  # Custom check interval and CSV file
  python salesforce_approval_bot.py --url "https://..." --interval 30 --csv my_rules.csv
  
  # Run for limited iterations (testing)
  python salesforce_approval_bot.py --url "https://..." --max-iterations 5
  
  # Run in visible mode (not headless)
  python salesforce_approval_bot.py --url "https://..." --no-headless
        """
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='Salesforce approval page URL'
    )
    parser.add_argument(
        '--csv',
        default='approvals_data.csv',
        help='CSV file with approval rules (default: approvals_data.csv)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Check interval in seconds (default: 10)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of checks (default: infinite)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode'
    )
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = SalesforceApprovalBot(
        csv_file=args.csv,
        headless=not args.no_headless
    )
    
    try:
        # Connect to Salesforce
        bot.connect_to_salesforce(args.url)
        
        # Start monitoring
        bot.monitor_and_approve(
            check_interval=args.interval,
            max_iterations=args.max_iterations
        )
    finally:
        bot.close()


if __name__ == '__main__':
    main()
