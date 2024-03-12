
#scrapy crawl top_movies -s CLOSESPIDER_PAGECOUNT=10 -o movies.jl

import scrapy

def convert_to_minutes(time_str):
        hours, minutes = 0, 0
        if 'h' in time_str:
            hours, remaining = time_str.split('h')
            hours = int(hours)
            if 'm' in remaining:
                minutes = int(remaining.split('m')[0])
        elif 'm' in time_str:
            minutes = int(time_str.split('m')[0])

        total_minutes = hours * 60 + minutes
        return total_minutes

def convert_to_float(currency_str):
    # Remove the dollar sign and the 'M'
    numeric_str = currency_str.replace('$', '').replace('M', '')

    # Convert to float
    return float(numeric_str)

class TopMoviesSpider(scrapy.Spider):
    name = 'top_movies'
    start_urls = ['https://editorial.rottentomatoes.com/guide/best-2023-movies/']


    

    def parse(self, response):
        # Extract the href attributes correctly
        href_links = response.css(".col-sm-6 a::attr(href)").getall()  # Use getall() to get a list of all matching elements
        for href in href_links:
            yield response.follow(href, self.parse_detail_page)

    
    def parse_detail_page(self, response):

        title = response.css("h1.title::text").get()
        if title:  # This checks if title is not None and not an empty string
            date_str = response.css("li.info-item:nth-child(7) > p:nth-child(1) > span:nth-child(2) > time:nth-child(1)::text").get()
            month =  date_str.split(' ')[0] if date_str else None
            rating_str = response.css("li.info-item:nth-child(1) > p:nth-child(1) > span:nth-child(2)::text").get() 
            rating =  rating_str.split(' ')[0] if date_str else None
            boxoffice = convert_to_float(response.css("li.info-item:nth-child(9) > p:nth-child(1) > span:nth-child(2)::text").get().strip().replace(" ", ""))

            minutes = convert_to_minutes(response.css("li.info-item:nth-child(10) > p:nth-child(1) > span:nth-child(2) > time:nth-child(1)::text").get().strip().replace(" ", ""))

            yield {
                "Title": title,  # This yields a dictionary with the key "Title" and its value
                "Boxoffice in Million": boxoffice,
                "Runtime in Minutes" : minutes,
                "Original Language": response.css("li.info-item:nth-child(3) > p:nth-child(1) > span:nth-child(2)::text").get().strip().replace(" ", ""),
                "Director": response.css("li.info-item:nth-child(4) > p:nth-child(1) > span:nth-child(2) > a:nth-child(1)::text").get().strip().replace(" ", ""),
                "release_month": month.strip().replace(" ", ""),
                "rating" : rating.strip().replace(" ", "")
                
                         

            }


                
