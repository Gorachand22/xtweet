# server.py
import asyncio
import sys
from playwright.async_api import async_playwright
from db import *
import time
import streamlit as st

async def post_tweet(news):
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=False)  # Launch normal browser
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://x.com/home")
            st.toast(f"Opened page: {page.url}")
            await asyncio.sleep(15)

            try:
                editor = await page.query_selector('div[class="DraftEditor-editorContainer"]')
            except:
                await page.goto("https://x.com/home")
                time.sleep(15)
                editor = await page.query_selector('div[class="DraftEditor-editorContainer"]')

            if editor:
                await editor.click()
                await asyncio.sleep(1)
                await page.keyboard.type(get_tweet(top_headline=news))
                await asyncio.sleep(2)

                await page.wait_for_selector('input[data-testid="fileInput"]')
                file_input = await page.query_selector('input[data-testid="fileInput"]')

                if file_input:
                    await file_input.set_input_files(get_tweet_image(top_headline=news))
                    st.toast("✅ Image uploaded successfully!")
                else:
                    st.toast("❌ File input not found.")

                await asyncio.sleep(2)
                await page.keyboard.press('Escape')
                await asyncio.sleep(1)
                await page.wait_for_selector('#layers', state='hidden', timeout=5000)

                post_button = await page.query_selector('button[data-testid="tweetButtonInline"]')
                if post_button and not await post_button.is_disabled():
                    await post_button.click(timeout=5000)
                    st.toast("✅ Tweet posted successfully!")
                else:
                    st.toast("❌ Tweet button not enabled.")
            else:
                st.toast("❌ Tweet editor not found.")
        except Exception as e:
            st.toast(f"❌ Error: {e}")
        finally:
            await browser.close()


def run_playwright(news=None):
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(post_tweet(news=news))
