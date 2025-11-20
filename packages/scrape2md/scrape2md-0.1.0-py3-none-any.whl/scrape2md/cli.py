#!/usr/bin/env python3
"""Command-line interface for scrape2md."""

import argparse
import os
from urllib.parse import urlparse

from . import __version__
from .scraper import WebScraper


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape websites to markdown with iframe support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scrape2md https://example.com
  scrape2md https://example.com -o output_folder -m 50 -d 2.0
  scrape2md url1.txt url2.txt url3.txt
        """
    )
    
    parser.add_argument(
        '--version', '-V',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        'urls',
        nargs='+',
        help='One or more URLs to scrape, or text files containing URLs'
    )
    parser.add_argument(
        '-o', '--output',
        default='scraped_sites',
        help='Base output directory (default: scraped_sites)'
    )
    parser.add_argument(
        '-m', '--max-pages',
        type=int,
        default=100,
        help='Maximum pages to scrape per site (default: 100)'
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--download-images',
        action='store_true',
        help='Download images (disabled by default for speed)'
    )
    
    args = parser.parse_args()
    
    # Collect all URLs
    all_urls = []
    for url_or_file in args.urls:
        if os.path.isfile(url_or_file):
            with open(url_or_file, 'r') as f:
                all_urls.extend([line.strip() for line in f if line.strip()])
        else:
            all_urls.append(url_or_file)
    
    if not all_urls:
        print("Error: No URLs provided")
        return
    
    print(f"Found {len(all_urls)} URL(s) to scrape\n")
    
    # Scrape each URL
    for idx, url in enumerate(all_urls, 1):
        print(f"\n{'='*70}")
        print(f"Processing {idx}/{len(all_urls)}: {url}")
        print(f"{'='*70}")
        
        # Create site-specific output directory
        parsed = urlparse(url)
        
        # Special handling for troopwebhost.org - use the path component as folder name
        if 'troopwebhost.org' in parsed.netloc:
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                site_name = path_parts[0]
            else:
                site_name = parsed.netloc.replace('.', '_')
        else:
            site_name = parsed.netloc.replace('.', '_')
        
        output_dir = os.path.join(args.output, site_name)
        
        scraper = WebScraper(
            base_url=url,
            output_dir=output_dir,
            max_pages=args.max_pages,
            delay=args.delay,
            download_images=args.download_images
        )
        
        try:
            scraper.scrape_site()
        except Exception as e:
            print(f"\nError scraping {url}: {e}")
            continue
    
    print(f"\n{'='*70}")
    print(f"All done! Scraped {len(all_urls)} site(s)")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

