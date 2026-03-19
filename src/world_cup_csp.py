import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """

        #Obtiene los equipos asignados al grupo
        teams_in_group = [t for t, g in assignment.items() if g == group]
        
        #Restricción de tamaño del grupo
        if len(teams_in_group) >= 4:
            return False
        
        #Restricción de bombo
        team_pot = self.get_team_pot(team)
        for t in teams_in_group:
            if self.get_team_pot(t) == team_pot:
                return False

        #Restricción de confederación
        team_conf = self.get_team_confederation(team)
        conf_count = {conf: 0 for conf in ["UEFA", "CONMEBOL", "CONCACAF", "AFC", "CAF", "OFC"]}
        
        for t in teams_in_group:
            conf_count[self.get_team_confederation(t)] += 1
        
        if team_conf == "UEFA":
            if conf_count["UEFA"] >= 2:
                return False
        else:
            if conf_count[team_conf] >= 1:
                return False
        
        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)

        for unassigned_team in self.variables:
            if unassigned_team not in assignment:
                valid_groups = []

                #Revisamos cada grupo en el dominio del equipo no asignado
                for group in new_domains[unassigned_team]:
                    if self.is_valid_assignment(group, unassigned_team, assignment):
                        valid_groups.append(group)

                #Actualizamos el dominio con los grupos válidos
                new_domains[unassigned_team] = valid_groups

                #Si el dominio queda vacío, la propagación falla
                if len(valid_groups) == 0:
                    return False, new_domains

        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """

        # Este es un valor de retorno por defecto
        unassigned_vars = [v for v in self.variables if v not in assignment]
        if not unassigned_vars:
            return None
        
        # Encontrar la variable con el dominio más pequeño
        mrv_var = min(unassigned_vars, key=lambda var: len(domains[var]))
        return mrv_var

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: Si todas las variables están asignadas, retornamos la asignación.
        if len(assignment) == len(self.variables):
            return assignment

        # Seleccionar la varaiable con MRV
        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return None
        
        #Iterar sobre los valores del dominio de la variable seleccionada
        for value in domains[var]:
            if self.is_valid_assignment(value, var, assignment):
                assignment[var] = value
                success, new_domains = self.forward_check(assignment, domains)
                if success:
                    result = self.backtrack(assignment, new_domains)
                    if result is not None:
                        return result
                del assignment[var]
    
        return None
