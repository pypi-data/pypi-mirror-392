class FeuRouge:
    def __init__(self, cycle=5):
        """
        Initialise un objet FeuRouge.
        """
        # TODO : initialiser le cycle et l'état du feu
        self.cycle = cycle
        self.etat_courant = 'rouge'
        self.debut_cycle = 0
        
    @property
    def etat(self):
        """Retourne l'état actuel du feu rouge"""
        # TODO : retourner l'état actuel ('rouge', 'vert', 'orange')
        return self.etat_courant
        
    #
    def avancer_temps(self, dt):
        """Fait avancer le temps de l'état du feu rouge de dt secondes et change l'état si nécessaire"""
        # TODO : faire avancer le temps et changer l'état si nécessaire
        self.debut_cycle += dt
        if self.debut_cycle >= self.cycle:
            self.etat_courant = 'vert' if self.etat_courant == 'rouge' else 'rouge'
            self.debut_cycle = 0
        