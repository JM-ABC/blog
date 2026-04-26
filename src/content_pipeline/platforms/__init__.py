from .instagram_cardnews import InstagramCardnewsGenerator
from .reels_scenario import ReelsScenarioGenerator
from .linkedin_post import LinkedinPostGenerator
from .blog_post import BlogPostGenerator
from .threads_post import ThreadsPostGenerator

PLATFORM_MAP = {
    "instagram": InstagramCardnewsGenerator,
    "reels": ReelsScenarioGenerator,
    "linkedin": LinkedinPostGenerator,
    "blog": BlogPostGenerator,
    "threads": ThreadsPostGenerator,
}

ALL_PLATFORMS = list(PLATFORM_MAP.keys())
