from collections import defaultdict
from urllib.parse import quote
from parsel import Selector
from scrapfly import ScrapeConfig, ScrapflyClient

scrapfly = ScrapflyClient("scp-live-c303a6f9a12f4b40913fa5df2c06bef5")

fraud_sites = ['booking', 'airbnb', 'funda', 'marktplaats']
#Dit is je exploitatiestand
woningen = ['Elzenlaan 10']

#Deze functie verwerkt het zoekwoord naar een gestructureerde datavorm voor verwerking
def parse_search_results(selector: Selector):
    """parse search results from google search page"""
    results = []
    for box in selector.xpath("//h1[contains(text(),'Search Results')]/following-sibling::div[1]/div"):
        title = box.xpath(".//h3/text()").get()
        url = box.xpath(".//h3/../@href").get()
        text = "".join(box.xpath(".//div[@data-content-feature=1]//text()").getall())
        if not title or not url:
            continue
        url = url.split("://")[1].replace("www.", "")
        results.append((title, url, text))
    return results

def scrape_search(query: str, page=1, country="NL"):
    """scrape search results for a given keyword"""
    # retrieve the SERP
    url = f"https://www.google.com/search?hl=en&q={quote(query)}" + (f"&start={10*(page-1)}" if page > 1 else "")
    print(f"scraping {query=} {page=}")
    results = defaultdict(list)
    result = scrapfly.scrape(ScrapeConfig(url, country=country, asp=True))
    # parse SERP for search result data
    results["search"].extend(parse_search_results(result.selector))
    return dict(results)

def act_on_fraud(fraud_site, woning):
    print('Woning ', woning, ' wordt aangeboden op website ', fraud_site)


#Loop over alle woningen in de eploitatiestand
for woning in woningen:
    #Loop over alle paginas van de google search
    for page in [1, 2]:
        results = scrape_search(woning, page=page)
        #Loop over alle zoekresultaten heen
        for result in results["search"]:
            #Controleer of de fraude trefwoorden voorkomen in de url
            for fraud_site in fraud_sites:
                if fraud_site in result[1]:
                    act_on_fraud(fraud_site, woning)
