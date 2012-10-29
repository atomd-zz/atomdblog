module Jekyll
  class ImageUrl < Liquid::Tag

    MATCHER_URL = /^\/(\w+)\/(.*)\/$/

    MATCHER_DATE = /(\d+)-(\d+)-(\d+)\s.+/

    def initialize(tag_name, img, tokens)
      super
      @orig_img = img.strip
    end

    def render(context)
      page_url = context.environments.first["page"]["url"]
      page_date = context.environments.first["page"]["date"]

      _, _, title = *page_url.match(MATCHER_URL)
      _, year, month, day = *page_date.to_s.match(MATCHER_DATE)
      return "/images/#{year}-#{month}-#{day}-#{title}/#{@orig_img}"

    end
  end
end

Liquid::Template.register_tag('image_url', Jekyll::ImageUrl)
