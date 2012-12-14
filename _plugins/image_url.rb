module Jekyll
  class ImageUrl < Liquid::Tag

    MATCHER_URL = /^\/(\w+)\/(.*)\/$/

    def initialize(tag_name, img, tokens)
      super
      @orig_img = img.strip
    end

    def render(context)
      page_url = context.environments.first["page"]["url"]
      _, _, title = *page_url.match(MATCHER_URL)
      return "/images/#{title}/#{@orig_img}"

    end
  end
end

Liquid::Template.register_tag('image_url', Jekyll::ImageUrl)
