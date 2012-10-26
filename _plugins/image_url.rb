module Jekyll
  class ImageUrl < Liquid::Tag
    MATCHER = /^\/(\w+)\/(\d+)\/(\d+)\/(\d+)\/(.*)\/$/

    def initialize(tag_name, img, tokens)
      super
      @orig_img = img.strip
    end

    def render(context)
      page_url = context.environments.first["page"]["url"]
      who, cares , year, month, day, title = *page_url.match(MATCHER)
      return "/images/#{year}-#{month}-#{day}-#{title}/#{@orig_img}"
    end
  end
end

Liquid::Template.register_tag('image_url', Jekyll::ImageUrl)
