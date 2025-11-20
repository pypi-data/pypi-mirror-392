"""
Test script for template rendering.

This script demonstrates how to render different templates with various configurations.
It supports rendering multiple templates with different data.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from dolze_image_templates import (
    get_template_registry,
    configure,
    get_font_manager,
)

# Initialize font manager to scan for fonts
font_manager = get_font_manager()
print("Font manager initialized. Available fonts:", font_manager.list_fonts())

# Configure the library
configure(
    templates_dir=os.path.join(
        os.path.dirname(__file__), "..", "dolze_image_templates", "html_templates"
    ),
    output_dir=os.path.join(os.path.dirname(__file__), "output"),
)


async def render_template(template_name, template_data):
    """Render a template with the provided data.

    Args:
        template_name (str): Name to use for the output file
        template_data (dict): Template data with custom content

    Returns:
        The rendered image
    """
    # Get the template registry
    registry = get_template_registry()

    # Render the template with the data
    output_path = os.path.join("output", f"{template_name}.png")
    rendered_image = await registry.render_template(
        template_name,  # Use the actual template name
        template_data,
        output_path=output_path,
    )

    print(f"Template saved to {os.path.abspath(output_path)}")
    return rendered_image


def get_faq_template_data():
    """Get sample data for the FAQ template."""
    return {
        "title": "FAQs",
        "question1": "How do I start a return or exchange?",
        "answer1": "Email us your order number to initiate the return or exchange process.",
        "question2": "What if I received a damaged item?",
        "answer2": "Send us photos right away. We'll arrange a replacement or full refund.",
        "question3": "How long does shipping take?",
        "answer3": "Standard shipping takes 3–7 business days. Express options (1–2 days) are available at checkout.",
        "question4": "Do you ship internationally?",
        "answer4": "Yes! We ship to over 40 countries. Duties and taxes may apply depending on your location.",
        "question5": "What is your return window?",
        "answer5": "You have 30 days from delivery to return unused items in original packaging for a full refund.",
        "question6": "How can I track my order?",
        "answer6": "You'll receive a tracking link via email as soon as your order ships. Check your inbox or spam folder.",
        "brand_name": "Dolze AI",
        "background_color": "#f8fbf8",
        "primary_text_color": "#0a3622",
        "title_color": "#0a6b42",
        "card_bg_color": "#0a6b42",
        "card_text_color": "#ffffff",
        "footer_text_color": "#0a3622",
        "brand_color": "#0a6b42",
        "shape_border_color": "rgba(10, 107, 66, 0.12)",
        "custom_css": "",
        "custom_html": ""
    }


def get_qa_template_data():
    """Get sample data for the Q&A template."""
    return {
        "question": "What is renewable energy?",
        "answer": "One wind turbine can power 1,500 homes annually!",
        "username": "@techcorp",
        "website_url": "techcorp.com",
        "theme_color": "#795548",
        "logo_url": "https://images.rawpixel.com/image_png_800/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDI0LTA3L2hpcHBvdW5pY29ybl9waG90b19vZl9kaXNzZWN0ZWRfZmxvYXRpbmdfdGFjb19zZXBhcmF0ZV9sYXllcl9vZl84M2Q0ODAwNC03MDc0LTRlZjItYjYyOC1jZTU3ODhiYzQxOGEucG5n.png"
    }


def get_spotlight_launching_data():
    """Get sample data for the spotlight launching template."""
    return {
        "main_title": "Launching Soon",
        "subheading": "Countdown",
        "days": "15",
        "hours": "08",
        "minutes": "45",
        "cta_text": "Stay Tuned!"
    }
def get_social_media_tips_template_data():
    """Get sample data for the social media tips template."""
    return {
        "title": "How to Grow Your Brand on Social Media",
        "tip1": "Determine a consistent upload schedule.",
        "tip2": "Understand your target demographic.",
        "tip3": "Keep track of social media analytics.",
        "tip4": "Encourage interaction with your posts.",
        "tip5": "Engage directly with your audience online.",
        "button_text": "Follow @reallygreatsite for more tips",
        "button_url": "#",
        "custom_css": "",
        "custom_html": ""
    }
def get_food_offer_promo_data():
    """Get sample data for the food offer promo template."""
    return {
        "product_image": "https://i.postimg.cc/PfZqsPcV/image-31.png",
        "product_name": "GRILLED CHICKEN",
        "product_description": "Description of the chicken dish and its ingredients",
        "price": "$14",
        "contact_text": "Contact us on ",
        "contact_number": "987 6543 3210",
        "address_line1": "123 STREET, AREA NAME",
        "address_line2": "YOUR CITY, STATE",
        "username": "@username",
        "theme_color": "#F4A300",
        "custom_css": "",
        "custom_html": ""
    }

def get_product_promotion_v2_data():
    """Get sample data for the product promotion v2 template."""
    return {
        "brand": "Dolze AI",
        "title": "GRILLED CHICKEN",
        "description": "Description of the chicken dish and its ingredients",
        "price": "$14",
        "contact_text": "Contact us on",
        "contact_phone": "987 6543 3210",
        "address_line1": "123 STREET, AREA NAME",
        "address_line2": "YOUR CITY, STATE",
        "product_image_url": "https://i.postimg.cc/PfZqsPcV/image-31.png",
        "background_color": "#ff9800",
        "price_bg_color": "#d60000",
        "price_text_color": "#ffffff",
        "text_color": "#000000",
        "custom_css": "",
        "custom_html": ""
    }

def get_testimonial_card_3_data():
    """Get sample data for the testimonial card 3 template."""
    return {
        "headline": "Testimonial",
        "author_name": "Olivia Wilson",
        "quote": "Social media can also be used to share interesting facts, inspiring true stories, helpful tips, useful knowledge, and other important information.",
        "author_role": "CEO of Ginyard International Co.",
        "company_name": "ReallyGreatCompany"
    }
def get_stocks_dividend_post_2_data():
    """Get sample data for the stocks dividend post 2 template."""
    return {
        "brand_name": "Stock.Academy",
        "title_line1": "What is a",
        "title_line2_accent": "Dividend Stock?",
        "body_text": "A dividend stock gives you regular income from company profits—paid out to shareholders. Think of it as your investment earning you 'rent' every quarter.",
    }

def get_spotlight_launching_text_3_data():
    """Get sample data for the spotlight launching text 3 template."""
    return {
        "main_title": "Launching Soon",
        "subtitle": "Get ready, because something amazing is coming your way!\nOur launch is just around the corner.",
        "website_url": "www.reallygreatsite.com",
        "custom_css": "",
        "custom_html": ""
    }

def get_search_services_listing_data():
    """Get sample data for the search services listing template."""
    return {
        "logo_url": "https://cdn.prod.website-files.com/65d0a7f29dc760c3869e2a2/65ec89c76f839f619b94dc55_refyne-dark-logo.svg",
        "brand_name": "Dolze AI",
        "search_placeholder": "Search our services...",
        "service1": "Online Payment Tracking",
        "service2": "Automatic Bank Feeds",
        "service3": "Collect Digital Payments",
        "service4": "Online Invoices & Quotes",
        "selected_service": "2",
        "hand_image_url": "https://i.ibb.co/example-hand.png",
        "cta_text": "reallygreatsite.com",
        "custom_css": ".service-item.item2 { background: #F3F4F6; }",
        "custom_html": ""
    }

def get_announcement_template_data():
    """Get sample data for the announcement template."""
    return {
        "primary_color": "#0A1D56",
        "header_text": "Official Announcement",
        "main_text": "We are\npartnering\nwith",
        "partner_text": "Rolk Inc.",
        "details_text": "More details on",
        "website_url": "www.reallygreatsite.com",
        "company_name": "WeisenhamTech",
        "custom_css": "",
        "custom_html": ""
    }

def get_customer_retention_strategies_data():
    """Get sample data for the customer retention strategies template."""
    return {
        "logo_letter": "D",
        "brand_name": "Dolze AI",
        "heading": "6 Strategies for",
        "title": "Customer Retention",
        "strategy1": "Make it simple\nand quick for\npeople to buy.",
        "strategy2": "Give good and\nuseful products\nwith help.",
        "strategy3": "Be kind, patient\nand helpful to\npeople.",
        "strategy4": "Make fun reward\nplans for happy\nbuyers.",
        "strategy5": "Always do what\nyou say you will\ndo about it.",
        "strategy6": "Ask happy\npeople to tell\nmore friends.",
        "footer_text": "www.dolze.ai",
        "custom_css": "",
        "custom_html": ""
    }

def get_hiring_minimal_red_data():
    """Get sample data for the hiring minimal red template."""
    return {
        "company_name": "Dolze AI",
        "hiring_title": "We're\nHiring",
        "role_title": "Marketers",
        "bullet1": "Do you have a passion for marketing?",
        "bullet2": "Do you have experience in marketing campaigns?",
        "bullet3": "Do you want to join a dynamic and innovative team?",
        "cta_text": "If yes, then apply now!",
        "apply_instruction": "Send your CV at email us:",
        "apply_email": "hello@reallygreatsite.com",
        "custom_css": "",
        "custom_html": ""
    }

def get_hiring_post_data():
    """Get sample data for the hiring post template."""
    return {
        "main_heading": "Join Our\nTeam",
        "intro_text": "Passionate about AI and business? We want you!",
        "hiring_prefix": "hiring",
        "job_title": "Social Media Lead",
        "company_name": "Dolze",
        "cta_text": "Apply Now!",
        "custom_css": "",
        "custom_html": ""
    }

def get_myth_or_fact_data():
    """Get sample data for the myth or fact template."""
    return {
        "main_title": "Myth or Fact\nSocial Media",
        "subtitle": "LET'S CLEAR UP COMMON SOCIAL MEDIA ASSUMPTIONS",
        "myth_heading": "Myth",
        "myth_item1": "You must post daily",
        "myth_item2": "More hashtags = more views",
        "myth_item3": "You need to go viral",
        "myth_item4": "Strategy = trend following",
        "fact_heading": "Fact",
        "fact_item1": "You must post daily",
        "fact_item2": "More hashtags = more views",
        "fact_item3": "You need to go viral",
        "fact_item4": "Strategy = trend following",
        "footer_text": "Reallygreatsite",   
        "custom_css": "",
        "custom_html": ""
    }

def get_perfect_job_search_data():
    """Get sample data for the perfect job search template."""
    return {
        "image_url": "https://images.pexels.com/photos/7691739/pexels-photo-7691739.jpeg",
        "logo_icon_url": "https://images.pexels.com/photos/2745478/pexels-photo-2745478.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=200",
        "logo_primary_text": "Business",
        "logo_secondary_text": "Agency",
        "headline": "Find The Perfect\nJob That You\nDeserve.",
        "subtitle": "Join thousands of professionals who found their dream career with us",
        "benefit1": "Expert career guidance",
        "benefit2": "Access to top companies",
        "cta_text": "reallygreatsite.com",
        "custom_css": "",
        "custom_html": ""
    }

def get_social_media_data():
    """Get sample data for the social media marketing template."""
    return {
        "brand_name": "Studio Shodwe",
        "main_heading": "Social Media\nMarketing",
        "tagline": "Transform your online presence with expert strategies",
        "benefit1": "Increased Visibility",
        "benefit2": "Better Engagement",
        "benefit3": "Higher Conversion Rates",
        "cta_main_text": "Visit Us For\nMore",
        "cta_website": "reallygreatsite.com",
        "photo_url": "https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg?auto=compress&cs=tinysrgb&w=800",
        "custom_css": "",
        "custom_html": ""
    }

def get_contact_us_overlay_data():
    """Get sample data for the contact us overlay template."""
    return {
        "background_image_url": "https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&cs=tinysrgb&w=1080",
        "brand_name": "Dolze AI",
        "main_heading": "Contact Us",
        "tagline": "Feel free to reach out to us!",
        "phone": "123-456-7890",
        "email": "hello@reallygreatsite.com",
        "website": "www.reallygreatsite.com",
        "address": "123 Anywhere St., Any City",
        "custom_css": "",
        "custom_html": ""
    }
def get_perfect_job_search_template_data():
    """Get sample data for the perfect job search template."""
    return {
        "image_url": "https://images.pexels.com/photos/7691739/pexels-photo-7691739.jpeg",
        "logo_icon_url": "https://images.pexels.com/photos/2745478/pexels-photo-2745478.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=200",
        "logo_primary_text": "Business",
        "logo_secondary_text": "Agency",
        "headline": "Find The Perfect\nJob That You\nDeserve.",
        "cta_text": "reallygreatsite.com",
        "supporting_text": "We Will Help You to Find The Most Suitable Job for You",
        "custom_css": "",
        "custom_html": ""
    }
def get_business_highlights_2035_html_data():
    """Get sample data for the business highlights 2035 html template."""
    return {
        "heading_word1": "BUSINESS",
        "heading_word2": "HIGHLIGHTS",
        "highlight1": "We are committed to providing the best possible service to our clients.",
        "highlight2": "We are committed to providing the best possible service to our clients.",
    }

def get_why_us_reasons_data():
    """Get sample data for the why us reasons template."""
    return {
        "site_name": "REALLYGREATSITE",
        "title_line1": "REASONS TO",
        "title_line2_part1": "CHOOSE",
        "title_line2_part2": "US:",
        "badge_text": "5 KEY REASONS",
        "reason1_title": "Expertise and Experience",
        "reason1_description": "Our team consists of seasoned professionals with specialized expertise to produce top-quality results.",
        "reason2_title": "Innovative Solutions",
        "reason2_description": "We utilize the latest technologies and creative strategies to deliver innovative and effective outcomes for your projects.",
        "reason3_title": "Customer-Centric Approach",
        "reason3_description": "We prioritize your needs and preferences, providing personalized solutions and exceptional customer service.",
        "reason4_title": "Reliability and Trust",
        "reason4_description": "We are dedicated to transparency, meeting deadlines, and fostering open communication to build a reliable partnership.",
        "reason5_title": "Competitive Pricing",
        "reason5_description": "We offer high-quality services at a competitive price, ensuring you get the best value for your investment.",
        "background_color": "#f8f4f0",
        "container_bg_color": "#fff",
        "primary_text_color": "#333",
        "secondary_text_color": "#666",
        "accent_color": "#ff5722",
        "line_color": "#ffccbc",
        "number_bg_color": "#fff",
        "number_text_color": "#ff5722",
        "custom_css": "",
        "custom_html": ""
    }

def get_smart_investment_data():
    """Get sample data for the smart investment template."""
    return {
        "company_name": "Ginyard International",
        "headline": "Smart Investment Now",
        "body_text": "A wise step to manage your future finances with the right, safe, and targeted strategy. By starting early, you can make your money work harder, build long-term wealth, and achieve financial freedom faster.",
        "sub_headline": "The Best Time to Invest Is Now",
        "cta_text": "More Infromation",
        "website_url": "www.reallygreatsite.com",
        "image_url": "https://images.pexels.com/photos/1181263/pexels-photo-1181263.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
    }

def get_pricing_plans_data():
    """Get sample data for the pricing plans template."""
    return {
        "company_name": "WARDIERE INC.",
        "logo_url": "https://i.postimg.cc/PfZqsPcV/image-31.png",
        "title": "Pricing Plans",
        "subtitle": "No matter your team size or experience level, our pricing adapts to your needs.",
        "starter_title": "Starter",
        "starter_description": "Perfect for individuals",
        "starter_feature1": "Basic features",
        "starter_feature2": "Email support",
        "starter_feature3": "1 user account",
        "starter_feature4": "Mobile app access",
        "starter_price": "$ 49/mo",
        "starter_extra": "Cancel anytime",
        "pro_title": "Pro",
        "pro_description": "Ideal for growing businesses",
        "pro_feature1": "Everything in Starter",
        "pro_feature2": "Priority support",
        "pro_feature3": "Up to 5 users",
        "pro_feature4": "Weekly reports",
        "pro_price": "$ 99/mo",
        "pro_extra": "24/7 customer support",
        "business_title": "Business",
        "business_description": "Tailored for teams with customizations",
        "business_feature1": "All Pro features",
        "business_feature2": "Account manager",
        "business_feature3": "Unlimited users",
        "business_feature4": "Advanced analytics",
        "business_price": "$ 149/mo",
        "business_extra": "7-day free trial",
      "cta_text": "Visit our website to explore the full list of features, detailed FAQs and plan comparisons. Let's take the next step and grow your business!",
      "website_url": "www.reallygreatsite.com",
      "accent_color": "#FFEB00",
      "custom_css": "",
      "custom_html": ""
  }

def get_we_are_hiring_data():
    """Get sample data for the we are hiring template."""
    return {
        "headline_primary": "WE ARE HIRING",
        "subheading_secondary": "Don't miss this opportunity",
        "role_list": "UI DESIGNER",
        "role_list_2": "FRONTEND DEVELOPER",
        "contact_email": "hello@reallygreatsite.com",
        "primary_color": "#233B35",
        "secondary_color": "#FFDE59",
        "custom_css": "",
        "custom_html": ""
    }

def get_flash_sale_data():
    """Get sample data for the flash sale template."""
    return {
        "brand_name": "Borcelle",
        "discount_percentage": "70",
        "days": "00",
        "hours": "00",
        "minutes": "00",
        "cta_text": "Shop Now Before It's Too Late!",
        "primary_color": "#d85028",
        "secondary_color": "#FFEB3B",
        "accent_color": "#5D4037",
        "custom_css": "",
        "custom_html": ""
    }

def get_creative_marketing_agency_data():
    """Get sample data for the creative marketing agency template."""
    return {
        "company_name": "Wardiere Inc.",
        "company_type": "Company",
        "heading_word1": "Creative",
        "heading_word2": "Marketing",
        "heading_word3": "Agency",
        "photo_url": "https://fjord.dropboxstatic.com/warp/conversion/dropbox/warp/en-us/resources/articles/collaborative-real-time-editing/TL_nzd2t5.jpg?id=109125be-848d-45e0-ad43-035e8555e410&width=1024&output_type=webp",
        "service1": "Branding and Identity Design",
        "service2": "Social Media Management",
        "service3": "Content Creation",
        "service4": "Digital Advertising",
        "phone_number": "+123-456-7890",
        "primary_color": "#1e3a52",
        "secondary_color": "#f5e6d3",
        "background_color": "#f9fafa",
        "custom_css": "",
        "custom_html": ""
    }

def get_quiz_2_data():
    """Get sample data for the quiz 2 template."""
    return {
        "background_color": "#1c1a44",
        "text_color": "#ffffff",
        "number_box_color": "#4d82b8",
        "option_background_color": "#c2e8e0",
        "logo_url": "https://cdn.prod.website-files.com/65d0a7f29d4c760c3869e2a2/65f1d3fea2483e3600d658f3_blue-logo.svg",
        "left_image_url": "https://www.bigfootdigital.co.uk/wp-content/uploads/2020/07/image-optimisation-scaled.jpg",
        "title_text": "Which financial service do you\nfind most essential for your needs?",
        "option1_label": "Retirement Planning",
        "option2_label": "Investment Management",
        "option3_label": "Debt Consolidation\nSolutions",
        "option4_label": "Financial Advisory\nServices",
        "footer_text": "@reallygreatwebsite",
        "custom_css": "",
        "custom_html": ""
    }

def get_quiz_3_data():
    """Get sample data for the quiz 3 template."""
    return {
        "background_color": "#1f1e1f",
        "text_color": "#ffffff",
        "logo_url": "https://cdn.prod.website-files.com/65d0a7f29d4c760c3869e2a2/65f1d3fea2483e3600d658f3_blue-logo.svg",
        "title_text": "WHICH IS MORE\nIMPORTANT FOR YOU?",
        "option1_label": "CONSISTENCY",
        "option2_label": "RELEVANCE",
        "footer_text": "@reallygreatsite",
        "options_box_background": "#2d2d2d",
        "options_box_border": "rgba(255,255,255,0.1)",
        "divider_color": "rgba(255,255,255,0.5)",
        "custom_css": "",
        "custom_html": ""
    }

def get_black_friday_offer_1_data():
    """Get sample data for the black friday offer 1 template."""
    return {
        "logo_url": "https://cdn.prod.website-files.com/65d0a7f29d4c760c3869e2a2/65ec89c76f839f619b94dc55_refyne-dark-logo.svg",
        "brand_name": "Refyne",
        "big_text_top": "BLACK",
        "big_text_bottom": "FRIDAY",
        "ribbon_text": "UP TO 50% OFF",
        "description": "From fashion to electronics, get everything you need at Black Friday prices!",
        "website": "www.reallygreatsite.com",
        "accent_primary_color": "#0066ff",
        "accent_secondary_color": "#ffffff",
        "background_color": "#000000",
        "custom_css": "",
        "custom_html": ""
    }

async def main():
    """Main async function to render all templates."""
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Define the templates to render
        templates = [
            # {"name": "partnership_announcement", "data": get_announcement_template_data()},
            # {"name": "social_media_tips", "data": get_social_media_tips_template_data()},
            # {"name": "testimonial_card", "data": get_testimonial_card_3_data()},
            # {"name": "contact_us", "data": get_contact_us_overlay_data()}
            # {"name": "job_search_promotion", "data": get_perfect_job_search_data()},
            # {"name": "hiring_announcement", "data": get_hiring_minimal_red_data()},
            # {"name": "strategy_cards", "data": get_customer_retention_strategies_data()},
            # {"name": "financial_education", "data": get_stocks_dividend_post_2_data()},
            # {"name": "services_showcase", "data": get_search_services_listing_data()},
            # {"name": "product_promotion", "data": get_food_offer_promo_data()},
            # {"name": "product_promotion_v2", "data": get_product_promotion_v2_data()},
            # {"name": "launch_announcement", "data": get_spotlight_launching_text_3_data()},
            # {"name": "job_opening", "data": get_hiring_post_data()},
            # {"name": "myth_vs_fact", "data": get_myth_or_fact_data()},
            # {"name": "service_promotion", "data": get_social_media_data()},
            # {"name":"annual_report", "data": get_business_highlights_2035_html_data()},
            # {"name": "why_us_reasons", "data": get_why_us_reasons_data()},
            # {"name": "faq_template", "data": get_faq_template_data()},
            # {"name": "smart_investment", "data": get_smart_investment_data()},
            # {"name": "pricing_plans", "data": get_pricing_plans_data()},
            # {"name": "we_are_hiring", "data": get_we_are_hiring_data()},
            # {"name": "flash_sale", "data": get_flash_sale_data()},
            # {"name": "creative_marketing_agency", "data": get_creative_marketing_agency_data()},
            # {"name": "quiz_2", "data": get_quiz_2_data()},
            {"name": "quiz_3", "data": get_quiz_3_data()},
            # {"name": "black_friday_offer_1", "data": get_black_friday_offer_1_data()},
        ]

        # {"name": "coming_soon_post_2", "data": get_coming_soon_post_2_data()},
        # Render each template
        for template in templates:
            await render_template(template["name"], template["data"])

        print("\nAll templates generated successfully!")
    except Exception as e:
        print(f"\nError generating templates: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
