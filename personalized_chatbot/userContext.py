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
    
    skills : list[str] = field(default_factory=lambda:[
        "Software Engineer",
        "Agentic AI Engineer",
        "Generative AI Engineer",
        "Nextjs Developer",
        "Modern Web App Developer"
    ])

    projects : list[dict[str, str]] = field(default_factory=lambda:[
        {
        "name" : "Mal Blogs",
        "description" : "A blogging website build with Nexjts, Tailwind CSS, Headless CMS (Contentfull)",
        "url" : "https://mal-blogs.vercel.app/"
        },

        {
            "name" : "User Gallery",
            "description" : "User can upload high resolution picture and can login too. It is build with nextjs, tailwind CSS, shadcn ui , typescript, and supabase",
            "url" : "https://user-gallery-website.vercel.app/"
        },

        {
            "name" : "Elygance",
            "description" : "An ecomerce store for fragrance. It is build with Nextjs, Tailwind CSS, Shadcn UI , Typescript, and Supabase",
            "url" : "https://elygance.vercel.app/"
        },

        {
            "name" : "MyScribe",
            "description": "Voice to text converter and record conversation between doctors and patient. It is build with Vuejs, Qusar Framework, Capacitor Mode, OpenAI , Laravel and MySQL."
        }
    ])


    services: list = field(default_factory=lambda: [
        "AI Agent Development with OpenAI SDK",
        "SaaS MVP Development (FastAPI + Supabase + Next.js)",
        "AI Integration in Web Apps",
        "Fullstack Development",
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

    @property
    def agent_instructions(self) -> str:
        """ System Instructions or Agent Persona"""
        return f""" You are special and personalize bot for {self.name} and you have this information {self.contact_info}. You are allowed to answer anything else. You just answer about {self.name} and all the data you have in your context.  """

    @property
    def about_me(self) -> str:
        f""" About {self.name}"""
        return f""" My name is  {self.name} and I am {self.age} years old. I am expert in {self.skills}. I have over 2 year of experice in  transoforming business ideas into digit solution."""


