from dataclasses import dataclass, field


@dataclass
class Person:
    name : str = field(default="Mustafa Tawab")
    age : int = field(default=24)
    location : str = field(default="Pakistan")
    email : str = field(default='tawab05@gmail.com')
    github : str = field(default="https://www.github.com/mustafatawab")
    linkedIn : str = field(default='https://www.linkedin.com/mustafa-tawab')
    fiverr : str = field(default="https://www.fiverr.com/mustafatawab")
    
    
    expertise : list[str] = field(default_factory=lambda:[
        "Agentic AI ",
        "Generative AI ",
        "Next.js and React.js",
        "Modern Python",
        "Backend Development",
        "Docker Containerization"
    ])

    projects : list[dict[str, str]] = field(default_factory=lambda:[
        {
        "title" : "Mal Blogs",
        "description" : "A blogging website build with Nexjts, Tailwind CSS, Headless CMS (Contentfull)",
        "url" : "https://mal-blogs.vercel.app/"
        },

        {
            "title" : "User Gallery",
            "description" : "User can upload high resolution picture and can login too. It is build with nextjs, tailwind CSS, shadcn ui , typescript, and supabase",
            "url" : "https://user-gallery-website.vercel.app/"
        },

        {
            "title" : "Elygance",
            "description" : "An ecomerce store for fragrance. It is build with Nextjs, Tailwind CSS, Shadcn UI , Typescript, and Supabase",
            "url" : "https://elygance.vercel.app/"
        },

        {
            "title" : "MyScribe",
            "description": "Voice to text converter and record conversation between doctors and patient. It is build with Vuejs, Qusar Framework, Capacitor Mode, OpenAI , Laravel and MySQL.",
            "url" : "https://www.app.myscribe.us"
        },
        {
            "title" : "Farsight System",
            "description" : "A software agency web application which are providing such software development solutions. This app has been created using Nextjs, Contentfull, Typescript, and Shadcn UI",
            "url" : "https://www.farsightsystem.com"
        }
    ])


    services: list = field(default_factory=lambda: [
        "Building Custom AI Agentts",
        "Custom Full Stack Web Applications",
        "AI Web Application",
        "Software Developement",
        "WordPress Solution",
        "Containerization & Deployment with Docker/Kubernetes"
    ])


        

    @property
    def contact_info(self) -> dict:
        """ Contact Information and All Information """
        return {
            "name" : self.name,
            "email" : self.email,
            "age" : self.age,
            "location": self.location,
            "github Url" : self.github,
            "linkedIn Url" : self.linkedIn,
            "fiverr profile" : self.fiverr
        }

    
