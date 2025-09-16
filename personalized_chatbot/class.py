class Company:
    
    def __init__(self, name: str, location : str, services : list[str]):
        self.name = name
        self.location= location
        self.services = services
    

    @property
    def projects(self):
        return [
            "Project A",
            "Project A",
            "Project A",
            "Project A",
            "Project A",
        ]
    


company = Company("farsitgh" , "swat" , ["Web" , "AI" , "S/W"])

print(company.projects)