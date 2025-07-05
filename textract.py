import random
import time

# --- Item Classes ---

class Item:
    """Base class for all items in the game."""
    def __init__(self, name, description, weight=1):
        self.name = name
        self.description = description
        self.weight = weight

    def __str__(self):
        return self.name

    def get_info(self):
        return f"{self.name}: {self.description} (Weight: {self.weight})"

class Weapon(Item):
    """Represents a weapon item."""
    def __init__(self, name, description, damage, weapon_type="ranged", weight=2, effective_range_type="medium"):
        super().__init__(name, description, weight)
        self.damage = damage
        self.weapon_type = weapon_type # "melee" or "ranged"
        self.effective_range_type = effective_range_type # "very_short", "short", "medium", "long"

    def get_info(self):
        return f"{super().get_info()}, Damage: {self.damage}, Type: {self.weapon_type}, Optimal Range: {self.effective_range_type.replace('_', ' ').capitalize()}"

class Armor(Item):
    """Represents an armor item."""
    def __init__(self, name, description, defense, slot="body", weight=3): # Added 'slot' attribute
        super().__init__(name, description, weight)
        self.defense = defense
        self.slot = slot # "body" or "head"

    def get_info(self):
        return f"{super().get_info()}, Defense: {self.defense}, Slot: {self.slot.capitalize()}"

class Consumable(Item):
    """Represents a consumable item (e.g., medkit, food)."""
    def __init__(self, name, description, effect_type, effect_value, weight=0.5):
        super().__init__(name, description, weight)
        self.effect_type = effect_type # "heal", "stamina_restore", "cure_bleeding"
        self.effect_value = effect_value

    def get_info(self):
        return f"{super().get_info()}, Effect: {self.effect_type.replace('_', ' ').capitalize()} ({self.effect_value})"

# --- Character Classes ---

class Character:
    """Base class for any character in the game (Player or Enemy)."""
    def __init__(self, name, max_health, current_health, damage, defense):
        self.name = name
        self.max_health = max_health
        self.current_health = current_health
        self.damage = damage
        self.defense = defense # Base defense, will be overridden by armor for player
        self.is_alive = True

    def take_damage(self, amount, hit_location="body"): # Added hit_location
        """Reduces character's health by a given amount, considering hit location."""
        # For generic characters (enemies), simplify defense application
        effective_damage = max(0, amount - self.defense)
        
        self.current_health -= effective_damage
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        return effective_damage

    def heal(self, amount):
        """Restores character's health by a given amount, up to max health."""
        self.current_health = min(self.max_health, self.current_health + amount)

    def __str__(self):
        return f"{self.name} (HP: {self.current_health}/{self.max_health})"

class Player(Character):
    """Represents the player character."""
    def __init__(self, name="PMC"):
        super().__init__(name, max_health=100, current_health=100, damage=5, defense=0)
        self.inventory = []
        self.max_inventory_weight = 50 # Example max weight
        self.equipped_weapon = None
        self.equipped_armor = None # Body armor
        self.equipped_helmet = None # New: Helmet slot
        self.max_stamina = 100
        self.current_stamina = 100
        self.is_bleeding = False # New status effect

    def get_current_weight(self):
        """Calculates the total weight of items in the inventory."""
        total_weight = sum(item.weight for item in self.inventory)
        if self.equipped_weapon:
            total_weight += self.equipped_weapon.weight
        if self.equipped_armor:
            total_weight += self.equipped_armor.weight
        if self.equipped_helmet: # Include helmet weight
            total_weight += self.equipped_helmet.weight
        return total_weight

    def add_item(self, item):
        """Adds an item to the player's inventory if weight allows."""
        if self.get_current_weight() + item.weight <= self.max_inventory_weight:
            self.inventory.append(item)
            print(f"You picked up {item.name}.")
            return True
        else:
            print(f"Your inventory is too full to pick up {item.name}.")
            return False

    def remove_item(self, item):
        """Removes an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            print(f"You dropped {item.name}.")
            return True
        return False

    def equip_weapon(self, weapon):
        """Equips a weapon, replacing any currently equipped weapon."""
        if not isinstance(weapon, Weapon):
            print(f"{weapon.name} cannot be equipped as a weapon.")
            return

        if self.equipped_weapon:
            self.inventory.append(self.equipped_weapon) # Move old weapon to inventory
            print(f"You unequipped {self.equipped_weapon.name}.")

        self.equipped_weapon = weapon
        if weapon in self.inventory:
            self.inventory.remove(weapon)
        self.damage = self.equipped_weapon.damage # Update player's base damage
        print(f"You equipped {weapon.name}.")

    def equip_armor(self, armor):
        """Equips armor (body or head), replacing any currently equipped item in that slot."""
        if not isinstance(armor, Armor):
            print(f"{armor.name} cannot be equipped as armor.")
            return

        if armor.slot == "body":
            if self.equipped_armor:
                self.inventory.append(self.equipped_armor) # Move old armor to inventory
                print(f"You unequipped {self.equipped_armor.name}.")
            self.equipped_armor = armor
            if armor in self.inventory:
                self.inventory.remove(armor)
            print(f"You equipped {armor.name} (Body).")
        elif armor.slot == "head":
            if self.equipped_helmet:
                self.inventory.append(self.equipped_helmet) # Move old helmet to inventory
                print(f"You unequipped {self.equipped_helmet.name}.")
            self.equipped_helmet = armor
            if armor in self.inventory:
                self.inventory.remove(armor)
            print(f"You equipped {armor.name} (Head).")
        else:
            print(f"Cannot equip {armor.name} to an unknown slot: {armor.slot}.")

    def use_consumable(self, consumable):
        """Uses a consumable item from inventory."""
        if not isinstance(consumable, Consumable):
            print(f"{consumable.name} is not a consumable item.")
            return False
        if consumable not in self.inventory:
            print(f"You don't have {consumable.name} in your inventory.")
            return False

        if consumable.effect_type == "heal":
            self.heal(consumable.effect_value)
            print(f"You used {consumable.name} and healed {consumable.effect_value} HP. Current HP: {self.current_health}/{self.max_health}")
        elif consumable.effect_type == "stamina_restore":
            self.current_stamina = min(self.max_stamina, self.current_stamina + consumable.effect_value)
            print(f"You used {consumable.name} and restored {consumable.effect_value} stamina. Current Stamina: {self.current_stamina}/{self.max_stamina}")
        elif consumable.effect_type == "cure_bleeding":
            if self.is_bleeding:
                self.is_bleeding = False
                print(f"You used {consumable.name} and stopped the bleeding.")
            else:
                print(f"You are not bleeding. {consumable.name} has no effect.")
                return False # Don't consume if not needed
        
        self.inventory.remove(consumable)
        return True

    def restore_stamina(self, amount):
        """Restores player's stamina."""
        self.current_stamina = min(self.max_stamina, self.current_stamina + amount)

    def display_stats(self):
        """Displays player's current stats."""
        print("\n--- Your Stats ---")
        print(f"Health: {self.current_health}/{self.max_health}")
        print(f"Stamina: {self.current_stamina}/{self.max_stamina}")
        print(f"Attack Damage: {self.damage} (Weapon: {self.equipped_weapon.name if self.equipped_weapon else 'None'})")
        print(f"Body Defense: {self.equipped_armor.defense if self.equipped_armor else 'None'} (Armor: {self.equipped_armor.name if self.equipped_armor else 'None'})")
        print(f"Head Defense: {self.equipped_helmet.defense if self.equipped_helmet else 'None'} (Helmet: {self.equipped_helmet.name if self.equipped_helmet else 'None'})")
        print(f"Inventory Weight: {self.get_current_weight()}/{self.max_inventory_weight}")
        print(f"Status: {'Bleeding' if self.is_bleeding else 'Normal'}")
        print("------------------")

    def display_inventory(self):
        """Displays player's inventory."""
        print("\n--- Your Inventory ---")
        if not self.inventory:
            print("Inventory is empty.")
        else:
            for i, item in enumerate(self.inventory):
                print(f"{i+1}. {item.get_info()}")
        print("----------------------")

    # Override take_damage to apply specific player defense and potentially inflict bleeding
    def take_damage(self, amount, hit_location="body"):
        defense_value = 0
        if hit_location == "head" and self.equipped_helmet:
            defense_value = self.equipped_helmet.defense
        elif hit_location == "body" and self.equipped_armor:
            defense_value = self.equipped_armor.defense
        
        effective_damage = max(0, amount - defense_value)
        
        # Apply headshot multiplier if head hit and no helmet
        if hit_location == "head" and not self.equipped_helmet:
            effective_damage = int(effective_damage * 1.5) # 1.5x damage for headshot without helmet

        self.current_health -= effective_damage
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        
        # Chance to bleed on taking damage, especially if headshot or high damage
        if effective_damage > 0 and (random.random() < 0.25 or (hit_location == "head" and not self.equipped_helmet)):
            if not self.is_bleeding:
                self.is_bleeding = True
                print("You are bleeding!")
        return effective_damage

class Enemy(Character):
    """Represents an enemy character."""
    def __init__(self, name, max_health, damage, defense, loot_items=None, equipped_weapon=None, equipped_armor=None, equipped_helmet=None, base_hit_chance=0.65): # Added base_hit_chance
        super().__init__(name, max_health, max_health, damage, defense) # Base defense
        self.loot_items = loot_items if loot_items is not None else []
        self.equipped_weapon = equipped_weapon
        self.equipped_armor = equipped_armor
        self.equipped_helmet = equipped_helmet
        self.base_hit_chance = base_hit_chance # Individual hit chance for enemy

    def get_condition(self):
        """Returns a string representing the enemy's health condition."""
        health_percentage = (self.current_health / self.max_health) * 100
        if health_percentage >= 75:
            return "Healthy"
        elif health_percentage >= 40:
            return "Wounded"
        elif health_percentage > 0:
            return "Critical"
        else:
            return "Dead"

    def take_damage(self, amount, hit_location="body"):
        """Reduces character's health by a given amount, considering hit location and equipped gear."""
        defense_value = self.defense # Base defense for enemy
        if hit_location == "head" and self.equipped_helmet:
            defense_value += self.equipped_helmet.defense
        elif hit_location == "body" and self.equipped_armor:
            defense_value += self.equipped_armor.defense
        
        effective_damage = max(0, amount - defense_value)
        
        # Enemies also take increased damage from headshots if no helmet
        if hit_location == "head" and not self.equipped_helmet:
            effective_damage = int(effective_damage * 2) # Double damage for headshot without helmet
            print(f"Critical hit on {self.name}'s head (no helmet)!")


        self.current_health -= effective_damage
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        return effective_damage

# --- Container Class ---
class Container:
    """Represents a lootable container in a location."""
    def __init__(self, name, description, items=None):
        self.name = name
        self.description = description
        self.items = items if items is not None else []
        self.is_looted = False

    def __str__(self):
        return self.name

    def get_info(self):
        status = " (Empty)" if not self.items and self.is_looted else ""
        return f"{self.name}: {self.description}{status}"

# --- Location Class ---

class Location:
    """Represents a location on the game map."""
    def __init__(self, name, description, is_extraction_point=False, range_type="medium"): # New range_type
        self.name = name
        self.description = description
        self.exits = {} # {direction: Location_object}
        self.items = [] # Items found directly in the location
        self.enemies = [] # Enemies currently in the location
        self.containers = [] # New: Containers in the location
        self.is_extraction_point = is_extraction_point
        self.visited = False # To track if player has been here before
        self.range_type = range_type # "close", "medium", "long"

    def add_exit(self, direction, destination_location):
        """Adds an exit to another location."""
        self.exits[direction] = destination_location

    def add_item(self, item):
        """Adds an item to the location."""
        self.items.append(item)

    def remove_item(self, item):
        """Removes an item from the location."""
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def add_enemy(self, enemy):
        """Adds an enemy to the location."""
        self.enemies.append(enemy)

    def remove_enemy(self, enemy):
        """Removes an enemy from the location."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            return True
        return False

    def add_container(self, container):
        """Adds a container to the location."""
        self.containers.append(container)

    def __str__(self):
        return self.name

# --- Game Class ---

class Game:
    """Manages the main game logic and flow."""
    def __init__(self):
        self.player = Player()
        self.map = {}
        self.current_location = None
        self.raid_timer = 100 # New: Max turns/actions before MIA
        # Define command aliases for easier input
        self.command_aliases = {
            "n": "move north", "e": "move east", "s": "move south", "w": "move west",
            "ne": "move northeast", "nw": "move northwest", "se": "move southeast", "sw": "move southwest",
            "inv": "inventory", "stat": "stats", "ex": "examine",
            "h": "help", "q": "quit", "l": "look"
        }
        self._create_map()
        self._initialize_game_state()
        self.game_over = False
        self.game_won = False

    def _create_map(self):
        """Initializes all locations and their connections."""
        # Create locations with specific range types
        customs_office = Location("Customs Office", "A dilapidated office building, once a customs checkpoint. Debris litters the floor.", range_type="close")
        dormitories = Location("Dormitories", "A cluster of abandoned dorm buildings, known for close-quarters combat and valuable loot.", range_type="close")
        factory_gate = Location("Factory Gate", "The main entrance to the old factory, heavily fortified and dangerous.", range_type="medium")
        woods_clearing = Location("Woods Clearing", "A quiet clearing in the dense woods, offering some cover but also open to long-range threats.", range_type="long")
        scav_camp = Location("Scav Camp", "A makeshift camp used by scavengers, often patrolled.", range_type="medium")
        old_gas_station = Location("Old Gas Station", "A rundown gas station, a common ambush point.", range_type="close")
        trailer_park = Location("Trailer Park", "A small, abandoned trailer park.", range_type="close")
        crossroads_extract = Location("Crossroads Extract", "A designated extraction point near the crossroads.", is_extraction_point=True, range_type="medium")
        z_b_013_extract = Location("ZB-013 Bunker", "An old military bunker, a reliable extraction point.", is_extraction_point=True, range_type="close")
        # New Locations for a bigger map
        construction_site = Location("Construction Site", "An unfinished building site, full of rebar and concrete. Good for cover, but easy to get lost.", range_type="close")
        power_station = Location("Power Station", "A derelict power station. High risk, high reward area.", range_type="medium")
        swamp = Location("Swamp", "A murky, overgrown swamp. Movement is slow, and visibility is low.", range_type="long")
        village = Location("Village", "An abandoned village with scattered houses. Potential for hidden loot.", range_type="close")
        rock_passage_extract = Location("Rock Passage Extract", "A narrow passage through rocks, another extraction point.", is_extraction_point=True, range_type="close")
        # Even more locations for variety and map size
        resort = Location("Resort", "A sprawling, abandoned health resort. High-tier loot, but extremely dangerous.", range_type="medium")
        shoreline_road = Location("Shoreline Road", "A long, exposed road running along the coast. Few places to hide.", range_type="long")
        lighthouse = Location("Lighthouse", "A tall lighthouse overlooking the sea. Excellent vantage point, but heavily guarded.", range_type="long")
        military_base = Location("Military Base", "A heavily fortified military installation. Extremely dangerous, but promises rare gear.", range_type="long")
        tunnel_extract = Location("Tunnel Extract", "A dark, winding tunnel leading out of the area.", is_extraction_point=True, range_type="close")


        # Add to map dictionary
        self.map = {
            "Customs Office": customs_office,
            "Dormitories": dormitories,
            "Factory Gate": factory_gate,
            "Woods Clearing": woods_clearing,
            "Scav Camp": scav_camp,
            "Old Gas Station": old_gas_station,
            "Trailer Park": trailer_park,
            "Crossroads Extract": crossroads_extract,
            "ZB-013 Bunker": z_b_013_extract,
            "Construction Site": construction_site,
            "Power Station": power_station,
            "Swamp": swamp,
            "Village": village,
            "Rock Passage Extract": rock_passage_extract,
            "Resort": resort,
            "Shoreline Road": shoreline_road,
            "Lighthouse": lighthouse,
            "Military Base": military_base,
            "Tunnel Extract": tunnel_extract,
        }

        # Define exits
        customs_office.add_exit("north", dormitories)
        customs_office.add_exit("east", factory_gate)
        customs_office.add_exit("south", old_gas_station)
        customs_office.add_exit("west", crossroads_extract)
        customs_office.add_exit("southeast", construction_site)

        dormitories.add_exit("south", customs_office)
        dormitories.add_exit("east", scav_camp)
        dormitories.add_exit("northwest", village)
        dormitories.add_exit("north", resort)

        factory_gate.add_exit("west", customs_office)
        factory_gate.add_exit("north", scav_camp)
        factory_gate.add_exit("east", power_station)
        factory_gate.add_exit("south", shoreline_road)

        woods_clearing.add_exit("south", trailer_park)
        woods_clearing.add_exit("east", scav_camp)
        woods_clearing.add_exit("northwest", z_b_013_extract)
        woods_clearing.add_exit("north", swamp)
        woods_clearing.add_exit("northeast", lighthouse)

        scav_camp.add_exit("west", dormitories)
        scav_camp.add_exit("south", factory_gate)
        scav_camp.add_exit("north", woods_clearing)
        scav_camp.add_exit("east", power_station)

        old_gas_station.add_exit("north", customs_office)
        old_gas_station.add_exit("east", trailer_park)
        old_gas_station.add_exit("south", construction_site)
        old_gas_station.add_exit("southwest", shoreline_road)

        trailer_park.add_exit("west", old_gas_station)
        trailer_park.add_exit("north", woods_clearing)
        trailer_park.add_exit("southwest", swamp)
        trailer_park.add_exit("south", military_base)

        crossroads_extract.add_exit("east", customs_office)

        z_b_013_extract.add_exit("southeast", woods_clearing)

        # New Location Exits
        construction_site.add_exit("northwest", customs_office)
        construction_site.add_exit("north", old_gas_station)
        construction_site.add_exit("east", power_station)
        construction_site.add_exit("south", rock_passage_extract)
        construction_site.add_exit("west", shoreline_road)

        power_station.add_exit("west", factory_gate)
        power_station.add_exit("southwest", construction_site)
        power_station.add_exit("west", scav_camp)
        power_station.add_exit("north", village)
        power_station.add_exit("east", lighthouse)

        swamp.add_exit("south", woods_clearing)
        swamp.add_exit("northeast", village)
        swamp.add_exit("east", trailer_park)
        swamp.add_exit("west", military_base)

        village.add_exit("south", dormitories)
        village.add_exit("southwest", power_station)
        village.add_exit("south", swamp)
        village.add_exit("east", resort)

        rock_passage_extract.add_exit("north", construction_site)

        resort.add_exit("south", dormitories)
        resort.add_exit("west", village)
        resort.add_exit("east", lighthouse)
        resort.add_exit("north", tunnel_extract)

        shoreline_road.add_exit("north", factory_gate)
        shoreline_road.add_exit("northeast", old_gas_station)
        shoreline_road.add_exit("east", construction_site)
        shoreline_road.add_exit("south", military_base)

        lighthouse.add_exit("southwest", woods_clearing)
        lighthouse.add_exit("west", resort)
        lighthouse.add_exit("south", power_station)

        military_base.add_exit("north", trailer_park)
        military_base.add_exit("east", shoreline_road)
        military_base.add_exit("northeast", swamp)
        military_base.add_exit("south", tunnel_extract)

        tunnel_extract.add_exit("south", resort)
        tunnel_extract.add_exit("north", military_base)


        self.current_location = customs_office # Starting location

    def _initialize_game_state(self):
        """Sets up initial items and enemies in the world."""
        # Define some common items
        pistol = Weapon("Makarov PM", "A basic 9x18mm pistol.", damage=15, weight=1.5, effective_range_type="short")
        ak74n = Weapon("AK-74N", "A reliable 5.45x39mm assault rifle.", damage=30, weight=4, effective_range_type="medium")
        shotgun = Weapon("MP-153", "A powerful 12-gauge shotgun.", damage=40, weight=3.5, effective_range_type="very_short")
        knife = Weapon("Combat Knife", "A sharp knife for close quarters.", damage=10, weapon_type="melee", weight=0.5, effective_range_type="very_short")
        mosin = Weapon("Mosin", "A bolt-action rifle, slow but powerful.", damage=50, weight=6, effective_range_type="long")
        mp5 = Weapon("MP5", "A fast-firing submachine gun.", damage=25, weight=3, effective_range_type="short")
        # New Weapons
        akm = Weapon("AKM", "A powerful 7.62x39mm assault rifle.", damage=35, weight=4.5, effective_range_type="medium")
        m4a1 = Weapon("M4A1", "A high-tech 5.56x45mm assault rifle.", damage=32, weight=3.8, effective_range_type="medium")
        svd = Weapon("SVD", "A long-range designated marksman rifle.", damage=60, weight=7, effective_range_type="long")

        paca_armor = Armor("PACA Body Armor", "Basic soft armor vest.", defense=5, slot="body", weight=5)
        kirasa_armor = Armor("Kirasa Armor", "Medium-grade body armor.", defense=10, slot="body", weight=8)
        gen4_armor = Armor("Gen4 Armor", "Heavy-duty modular armor.", defense=15, slot="body", weight=12)
        # New Helmets
        ssh68_helmet = Armor("SSh-68 Helmet", "A basic steel helmet.", defense=3, slot="head", weight=2)
        kolpak_helmet = Armor("Kolpak-1 Helmet", "A simple protective helmet.", defense=5, slot="head", weight=3)
        altyn_helmet = Armor("Altyn Helmet", "Heavy-duty titanium helmet with faceshield.", defense=12, slot="head", weight=7)

        medkit = Consumable("AI-2 Medkit", "A basic medical kit.", effect_type="heal", effect_value=50, weight=0.5)
        painkillers = Consumable("Painkillers", "Reduces pain, restores some stamina.", effect_type="stamina_restore", effect_value=30, weight=0.2)
        water_bottle = Consumable("Water Bottle", "Quenches thirst.", effect_type="stamina_restore", effect_value=20, weight=0.3)
        # Changed bandage effect_type to cure_bleeding
        bandage = Consumable("Bandage", "Stops light bleeding.", effect_type="cure_bleeding", effect_value=0, weight=0.1)
        esmarch = Consumable("Esmarch Tourniquet", "Stops heavy bleeding.", effect_type="cure_bleeding", effect_value=0, weight=0.1)
        # New Consumables
        grizzly_medkit = Consumable("Grizzly Medkit", "A comprehensive medical kit.", effect_type="heal", effect_value=100, weight=1.5)
        energy_drink = Consumable("Energy Drink", "Boosts stamina significantly.", effect_type="stamina_restore", effect_value=50, weight=0.3)

        # --- BEAR PMC Starting Equipment ---
        # More competitive starting gear for a BEAR PMC
        self.player.add_item(akm) # Start with an AKM
        self.player.equip_weapon(akm)
        self.player.add_item(kirasa_armor) # Start with Kirasa armor
        self.player.equip_armor(kirasa_armor)
        self.player.add_item(kolpak_helmet) # Start with Kolpak helmet
        self.player.equip_armor(kolpak_helmet)
        self.player.add_item(medkit)
        self.player.add_item(medkit) # Two medkits
        self.player.add_item(bandage)
        self.player.add_item(esmarch) # Start with an Esmarch for bleeding
        self.player.add_item(painkillers) # Start with painkillers


        # Place some static loot
        self.map["Dormitories"].add_item(ak74n)
        self.map["Dormitories"].add_item(medkit)
        self.map["Factory Gate"].add_item(shotgun)
        self.map["Scav Camp"].add_item(paca_armor)
        self.map["Old Gas Station"].add_item(painkillers)
        self.map["Woods Clearing"].add_item(water_bottle)
        self.map["Trailer Park"].add_item(kirasa_armor)
        self.map["Construction Site"].add_item(mosin)
        self.map["Power Station"].add_item(gen4_armor)
        self.map["Village"].add_item(mp5)
        self.map["Swamp"].add_item(esmarch)
        # New static loot locations
        self.map["Resort"].add_item(m4a1)
        self.map["Resort"].add_item(altyn_helmet)
        self.map["Military Base"].add_item(svd)
        self.map["Military Base"].add_item(grizzly_medkit)
        self.map["Lighthouse"].add_item(akm)
        self.map["Shoreline Road"].add_item(kolpak_helmet)
        self.map["Shoreline Road"].add_item(energy_drink)


        # Add containers with loot
        self.map["Dormitories"].add_container(Container("Duffle Bag", "A worn-out duffle bag.", items=[painkillers, Item("Spark Plug", "A small engine part.", weight=0.1)]))
        self.map["Factory Gate"].add_container(Container("Wooden Crate", "A sturdy wooden crate, probably used for shipping.", items=[bandage, Item("Wires", "A coil of electrical wires.", weight=0.2)]))
        self.map["Power Station"].add_container(Container("Weapon Box", "A military-grade weapon box.", items=[ak74n, Item("Ammunition", "5.45x39mm rounds.", weight=0.3)]))
        self.map["Village"].add_container(Container("Shed Stash", "A hidden stash in an old shed.", items=[medkit, Item("Valuable Item", "A rare and valuable trinket.", weight=0.5)]))
        # New containers
        self.map["Resort"].add_container(Container("Medical Bag", "A large medical bag.", items=[grizzly_medkit, esmarch, Consumable("Morphine", "Strong painkiller.", effect_type="stamina_restore", effect_value=40, weight=0.1)]))
        self.map["Military Base"].add_container(Container("Weapon Crate", "A sealed military weapon crate.", items=[m4a1, svd, Item("Grenade", "A fragmentation grenade.", weight=0.4)]))
        self.map["Lighthouse"].add_container(Container("Supply Cache", "A small, waterproof supply cache.", items=[akm, Item("Gold Chain", "A valuable gold chain.", weight=0.1)]))


        # Define common loot items for scavs
        self.scav_common_loot = [
            Item("Wrench", "A rusty wrench.", weight=1),
            Item("Matches", "A box of matches.", weight=0.1),
            Consumable("Chocolate Bar", "A sugary treat.", effect_type="stamina_restore", effect_value=10, weight=0.1),
            Consumable("MRE", "Meal Ready-to-Eat.", effect_type="heal", effect_value=30, weight=0.8),
            Consumable("Bandage", "Stops light bleeding.", effect_type="cure_bleeding", effect_value=0, weight=0.1)
        ]
        # Define common weapons scavs might carry
        self.scav_weapons = [
            pistol, # Makarov PM
            Weapon("MP-133 Shotgun", "A pump-action 12-gauge shotgun.", damage=30, weight=3, effective_range_type="very_short"),
            Weapon("SKS", "A semi-automatic 7.62x39mm carbine.", damage=28, weight=3.8, effective_range_type="medium"),
            Weapon("Vepr KM", "A civilian AK variant.", damage=32, weight=4.2, effective_range_type="medium")
        ]
        # Define common armor/helmets scavs might wear
        self.scav_armor_pieces = [
            paca_armor,
            Armor("6B23-1 Armor", "Standard issue body armor.", defense=8, slot="body", weight=7),
            None # Chance for no body armor
        ]
        self.scav_helmets = [
            ssh68_helmet,
            kolpak_helmet,
            Armor("Comtacs", "Tactical headset.", defense=1, slot="head", weight=0.5), # Low defense "helmet"
            None # Chance for no helmet
        ]

        # Define better gear for armored scavs
        self.armored_scav_weapons = [ak74n, akm, mp5, shotgun, mosin]
        self.armored_scav_armor = [kirasa_armor, gen4_armor]
        self.armored_scav_helmets = [kolpak_helmet, altyn_helmet, ssh68_helmet] # Higher chance for better helmets


        # Initial enemy spawns (some fixed, some random)
        # Killa
        killa_weapon = m4a1 # Example weapon for Killa
        killa_armor = gen4_armor
        killa_helmet = altyn_helmet
        self.map["Resort"].add_enemy(Enemy("Killa", 200, 40, 0, # Base defense 0, armor adds
                                            loot_items=[altyn_helmet, gen4_armor, m4a1, grizzly_medkit],
                                            equipped_weapon=killa_weapon, equipped_armor=killa_armor, equipped_helmet=killa_helmet,
                                            base_hit_chance=0.85)) # Killa is accurate

        # Glukhar
        glukhar_weapon = svd # Example weapon for Glukhar
        glukhar_armor = gen4_armor
        glukhar_helmet = altyn_helmet # Glukhar could have a different helmet, or none. Let's give him Altyn for now.
        self.map["Military Base"].add_enemy(Enemy("Glukhar", 250, 45, 0, # Base defense 0, armor adds
                                            loot_items=[svd, gen4_armor, akm, grizzly_medkit, Item("Keycard", "A valuable keycard.", weight=0.05)],
                                            equipped_weapon=glukhar_weapon, equipped_armor=glukhar_armor, equipped_helmet=glukhar_helmet,
                                            base_hit_chance=0.90)) # Glukhar is very accurate

        # Other fixed enemies - ensure they also have equipped gear
        self.map["Dormitories"].add_enemy(Enemy("Scav Raider", 80, 20, 0, loot_items=[ak74n, medkit, painkillers],
                                            equipped_weapon=ak74n, equipped_armor=kirasa_armor, equipped_helmet=kolpak_helmet,
                                            base_hit_chance=0.75)) # Scav Raider is also accurate
        self.map["Factory Gate"].add_enemy(Enemy("Heavy Scav", 120, 25, 0, loot_items=[shotgun, kirasa_armor],
                                            equipped_weapon=shotgun, equipped_armor=gen4_armor, equipped_helmet=ssh68_helmet,
                                            base_hit_chance=0.70))
        self.map["Power Station"].add_enemy(Enemy("Cultist", 150, 35, 0, loot_items=[gen4_armor, mosin, esmarch],
                                            equipped_weapon=mosin, equipped_armor=kirasa_armor, equipped_helmet=None,
                                            base_hit_chance=0.80)) # Cultists are stealthy and precise

        self._spawn_random_enemies()

    def _spawn_random_enemies(self):
        """Randomly spawns basic scavs in unvisited locations, and occasionally in visited ones."""
        
        spawned_in_current_location = False

        for loc_name, location in self.map.items():
            # Only spawn if no enemies are currently there and it's not an extraction point
            if not location.enemies and not location.is_extraction_point:
                # Higher chance in unvisited, moderate chance in visited
                spawn_chance = 0.4 if not location.visited else 0.15
                if random.random() < spawn_chance:
                    num_scavs = random.randint(1, 2)
                    for _ in range(num_scavs):
                        # Determine enemy type and gear
                        if random.random() < 0.25: # 25% chance for an Armored Scav
                            enemy_name = "Armored Scav"
                            enemy_health = random.randint(70, 90)
                            enemy_damage = random.randint(18, 22)
                            enemy_defense = 0 # Base defense, armor will add to this
                            enemy_base_hit_chance = 0.45 # Decreased for random enemies

                            # Armored Scav specific loot
                            enemy_loot = random.sample(self.scav_common_loot, random.randint(1, 3))
                            equipped_weapon = random.choice(self.armored_scav_weapons)
                            enemy_loot.append(equipped_weapon) # Always drop a weapon
                            
                            # Ensure armored scavs have armor and possibly a helmet
                            equipped_armor = random.choice(self.armored_scav_armor)
                            equipped_helmet = random.choice(self.armored_scav_helmets)

                            new_enemy = Enemy(enemy_name, enemy_health, enemy_damage, enemy_defense, 
                                              loot_items=enemy_loot, equipped_weapon=equipped_weapon,
                                              equipped_armor=equipped_armor, equipped_helmet=equipped_helmet,
                                              base_hit_chance=enemy_base_hit_chance)
                            location.add_enemy(new_enemy)
                            if location == self.current_location:
                                print(f"An {enemy_name} lurks nearby...")
                                spawned_in_current_location = True
                        else: # Regular Scav
                            enemy_name = "Scav"
                            enemy_health = random.randint(40, 60)
                            enemy_damage = random.randint(10, 15)
                            enemy_defense = 0 # Base defense, armor will add to this
                            enemy_base_hit_chance = 0.45 # Decreased for random enemies

                            # Regular Scav specific loot
                            enemy_loot = random.sample(self.scav_common_loot, random.randint(0, 2))
                            equipped_weapon = random.choice(self.scav_weapons)
                            enemy_loot.append(equipped_weapon) # Always drop a weapon

                            equipped_armor = random.choice(self.scav_armor_pieces)
                            equipped_helmet = random.choice(self.scav_helmets)

                            new_enemy = Enemy(enemy_name, enemy_health, enemy_damage, enemy_defense, 
                                              loot_items=enemy_loot, equipped_weapon=equipped_weapon,
                                              equipped_armor=equipped_armor, equipped_helmet=equipped_helmet,
                                              base_hit_chance=enemy_base_hit_chance)
                            location.add_enemy(new_enemy)
                            if location == self.current_location:
                                print(f"A {enemy_name} lurks nearby...")
                                spawned_in_current_location = True
        if spawned_in_current_location:
            print("You hear movement nearby...")


    def display_location(self):
        """Displays information about the current location."""
        print(f"\n--- You are in the {self.current_location.name} ---")
        print(self.current_location.description)
        print(f"Combat Range: {self.current_location.range_type.capitalize()}") # Display range

        if self.current_location.items:
            print("\nItems on the ground:")
            for item in self.current_location.items:
                print(f"- {item.get_info()}")

        if self.current_location.containers:
            print("\nContainers present:")
            for container in self.current_location.containers:
                print(f"- {container.get_info()}")

        if self.current_location.enemies:
            print("\nEnemies present:")
            for enemy in self.current_location.enemies:
                print(f"- {enemy.name}") # Only show name, condition revealed in combat if close
        else:
            print("\nNo enemies detected.")

        print("\nExits:")
        for direction, location in self.current_location.exits.items():
            print(f"- {direction.capitalize()} to {location.name}")
        print("-----------------------------------")
        self.current_location.visited = True # Mark as visited after displaying

    def _fuzzy_find_item_in_lists(self, item_name_input, item_lists_to_search):
        """
        Helper function to perform fuzzy matching for items across multiple lists.
        Returns the matched item, or None if no unique match or user cancels.
        """
        all_possible_items = []
        for item_list in item_lists_to_search:
            # Ensure item_list is iterable and not None
            if isinstance(item_list, list):
                all_possible_items.extend(item_list)
            elif item_list is not None: # Handle single items passed as non-list
                all_possible_items.append(item_list)
        
        matches = []
        for item in all_possible_items:
            if item and item.name.lower().startswith(item_name_input.lower()):
                matches.append(item)
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"Multiple items match '{item_name_input}':")
            for i, item in enumerate(matches):
                print(f"{i+1}. {item.name}")
            while True:
                try:
                    choice = input("Enter the number of the item you want, or 'cancel': ").strip().lower()
                    if choice == 'cancel':
                        return None
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(matches):
                        return matches[choice_idx]
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input. Please enter a number or 'cancel'.")
        return None

    def handle_input(self, command):
        """Processes player commands, including command aliases and partial completion."""
        original_command = command.lower().strip()
        
        # Check for direct aliases (e.g., 'n' for 'move north')
        if original_command in self.command_aliases:
            command = self.command_aliases[original_command]
        else:
            # Attempt partial completion for main commands
            main_commands = ["move", "look", "get", "drop", "equip", "use", "attack", "inventory", "stats", "search", "extract", "help", "quit", "examine", "rest", "flee"] # Added "rest", "flee"
            command_parts = original_command.split(maxsplit=1)
            action_prefix = command_parts[0]
            
            matching_commands = [cmd for cmd in main_commands if cmd.startswith(action_prefix)]

            if len(matching_commands) == 1:
                # If a unique partial match, use it
                command = matching_commands[0] + (" " + (command_parts[1] if len(command_parts) > 1 else ""))
                print(f"(Autocompleted to: {command})")
            elif len(matching_commands) > 1:
                print(f"Ambiguous command. Did you mean: {', '.join(matching_commands)}?")
                return # Don't process this turn if ambiguous
            # If no match or multiple matches, proceed with original command (might be invalid)

        command_parts = command.split(maxsplit=1)
        action = command_parts[0]
        arg = command_parts[1] if len(command_parts) > 1 else ""

        # Flag to check if a valid action was performed
        valid_action_performed = False

        if action == "move":
            self.move_player(arg)
            valid_action_performed = True
        elif action == "look":
            self.display_location()
            valid_action_performed = True
        elif action == "get":
            self.get_item(arg)
            valid_action_performed = True
        elif action == "drop":
            self.drop_item(arg)
            valid_action_performed = True
        elif action == "equip":
            self.equip_item(arg)
            valid_action_performed = True
        elif action == "use":
            self.use_item(arg)
            valid_action_performed = True
        elif action == "attack":
            self.attack_enemy(arg)
            valid_action_performed = True
        elif action == "inventory" or action == "inv":
            self.player.display_inventory()
            valid_action_performed = True
        elif action == "stats":
            self.player.display_stats()
            valid_action_performed = True
        elif action == "search":
            self.search_container(arg)
            valid_action_performed = True
        elif action == "examine":
            self.examine_item(arg)
            valid_action_performed = True
        elif action == "rest": # New rest action
            self.rest_player()
            valid_action_performed = True
        elif action == "flee": # New flee action
            # Flee command is handled within combat_round, so it doesn't directly decrement timer here
            # But if it's called outside combat, it's invalid.
            print("You can only 'flee' during combat.")
            # valid_action_performed remains False
        elif action == "extract":
            self.check_extraction()
            valid_action_performed = True
        elif action == "help":
            self.display_help()
            valid_action_performed = True
        elif action == "quit":
            self.game_over = True
            valid_action_performed = True
        else:
            print("Invalid command. Type 'help' for a list of commands.")
            # valid_action_performed remains False, so timer won't decrement

        # Decrement raid timer ONLY if a valid action was performed and it's not 'quit'
        if valid_action_performed and action != "quit":
            self.raid_timer -= 1
            if self.raid_timer <= 0:
                print("\nTime is up, PMC! You are Missing in Action (MIA). Raid failed!")
                self.game_over = True
                return

        # Apply bleeding damage if player is bleeding (happens at end of turn, regardless of command validity)
        if self.player.is_bleeding:
            bleeding_damage = random.randint(2, 5)
            self.player.take_damage(bleeding_damage, hit_location="body") # Bleeding is body damage
            print(f"You are bleeding, taking {bleeding_damage} damage. Current HP: {self.player.current_health}/{self.player.max_health}")


    def display_help(self):
        """Displays available commands."""
        print("\n--- Available Commands ---")
        print("move [direction] (or n/e/s/w/ne/nw/se/sw) - Move to an adjacent location.")
        print("look (or l) - Re-examine your current location.")
        print("get [item name] - Pick up an item from the ground.")
        print("drop [item name] - Drop an item from your inventory.")
        print("equip [item name] - Equip a weapon, body armor, or helmet from your inventory.")
        print("use [item name] - Use a consumable item from your inventory.")
        print("attack [enemy name] - Attack an enemy in the current location.")
        print("inventory (or inv) - View your inventory.")
        print("stats (or stat) - View your player stats.")
        print("search [container name] - Search a container in the current location.")
        print("examine [item name] (or ex) - View detailed information about an item in your inventory.")
        print("rest - Take a moment to recover stamina.") # New help entry
        print("flee [direction] - Attempt to escape combat in a specific direction.") # New help entry
        print("extract - Attempt to extract from the raid.")
        print("help (or h) - Display this list of commands.")
        print("quit (or q) - Exit the game.")
        print("--------------------------")

    def move_player(self, direction):
        """Moves the player to a new location if the exit exists and initiates combat if enemies are present."""
        stamina_cost = 15 # Stamina cost for moving
        if self.player.current_stamina < stamina_cost:
            print(f"You don't have enough stamina to move! You need {stamina_cost} stamina.")
            return False # Indicate that move failed due to stamina

        if direction in self.current_location.exits:
            new_location = self.current_location.exits[direction]
            print(f"Moving {direction} to {new_location.name}...")
            self.player.current_stamina -= stamina_cost # Subtract stamina
            self.current_location = new_location
            self._spawn_random_enemies() # Attempt to spawn enemies on entering new location
            self.player.restore_stamina(5) # Passive stamina regen on movement
            self.display_location()

            # Check for enemies and initiate combat immediately
            if self.current_location.enemies:
                print("\nYou are ambushed! Enemies are present and engaging!")
                # Fight enemies one by one until all are defeated or player is dead
                enemies_to_fight = list(self.current_location.enemies) # Create a copy to iterate
                for enemy in enemies_to_fight:
                    if self.player.is_alive and enemy.is_alive:
                        # Re-added the call to attack_enemy to initiate combat
                        self.attack_enemy(enemy.name) 
                    if not self.player.is_alive: # Break if player dies during combat
                        break
                if self.player.is_alive:
                    print("You have cleared the immediate threat.")
            return True # Indicate successful move
        else:
            print(f"You cannot go {direction} from here.")
            return False # Indicate that move failed due to invalid direction

    def get_item(self, item_name_input): # Renamed from take_item
        """Attempts to pick up an item from the current location using fuzzy matching."""
        found_item = self._fuzzy_find_item_in_lists(item_name_input, [self.current_location.items])
        
        if found_item:
            if self.player.add_item(found_item):
                self.current_location.remove_item(found_item)
        else:
            print(f"There is no '{item_name_input}' here, or your input was ambiguous.")

    def drop_item(self, item_name_input):
        """Attempts to drop an item from the player's inventory using fuzzy matching."""
        found_item = self._fuzzy_find_item_in_lists(item_name_input, [self.player.inventory])

        if found_item:
            if self.player.remove_item(found_item):
                self.current_location.add_item(found_item)
        else:
            print(f"You don't have '{item_name_input}' in your inventory, or your input was ambiguous.")

    def equip_item(self, item_name_input):
        """Attempts to equip an item from the player's inventory using fuzzy matching."""
        found_item = self._fuzzy_find_item_in_lists(item_name_input, [self.player.inventory])

        if found_item:
            if isinstance(found_item, Weapon):
                self.player.equip_weapon(found_item)
            elif isinstance(found_item, Armor):
                self.player.equip_armor(found_item) # This now handles both body and head armor
            else:
                print(f"{found_item.name} cannot be equipped.")
        else:
            print(f"You don't have '{item_name_input}' in your inventory to equip, or your input was ambiguous.")

    def use_item(self, item_name_input):
        """Attempts to use a consumable item from the player's inventory using fuzzy matching."""
        found_item = self._fuzzy_find_item_in_lists(item_name_input, [self.player.inventory])

        if found_item:
            self.player.use_consumable(found_item)
        else:
            print(f"You don't have '{item_name_input}' in your inventory to use, or your input was ambiguous.")

    def examine_item(self, item_name_input):
        """Displays detailed information about an item using fuzzy matching."""
        player_accessible_items = list(self.player.inventory)
        if self.player.equipped_weapon:
            player_accessible_items.append(self.player.equipped_weapon)
        if self.player.equipped_armor:
            player_accessible_items.append(self.player.equipped_armor)
        if self.player.equipped_helmet:
            player_accessible_items.append(self.player.equipped_helmet)

        found_item = self._fuzzy_find_item_in_lists(item_name_input, [player_accessible_items])

        if found_item:
            print(f"\n--- Examining {found_item.name} ---")
            print(found_item.get_info())
            print("-----------------------------")
        else:
            print(f"You don't have '{item_name_input}' to examine, or your input was ambiguous.")

    def search_container(self, container_name_input): # Added fuzzy matching
        """Searches a container in the current location for loot using fuzzy matching."""
        target_container = self._fuzzy_find_item_in_lists(container_name_input, [self.current_location.containers])
        
        if not target_container:
            print(f"There is no '{container_name_input}' here to search, or your input was ambiguous.")
            return

        if target_container.is_looted:
            print(f"The {target_container.name} is already empty.")
            return

        if not target_container.items:
            print(f"You search the {target_container.name}, but it's empty.")
            target_container.is_looted = True
            return

        print(f"You search the {target_container.name} and find:")
        for item in list(target_container.items): # Iterate over a copy to allow modification
            if self.player.add_item(item):
                target_container.items.remove(item)
            else:
                print(f"You couldn't pick up {item.name} due to inventory weight.")
        
        if not target_container.items:
            target_container.is_looted = True
            print(f"The {target_container.name} is now empty.")
        else:
            print(f"Some items remain in the {target_container.name}.")

    def rest_player(self):
        """Restores player's stamina."""
        if self.player.current_stamina == self.player.max_stamina:
            print("You are already at full stamina.")
        else:
            stamina_restored = 40 # Fixed amount for resting
            self.player.restore_stamina(stamina_restored)
            print(f"You rest for a moment, restoring {stamina_restored} stamina. Current Stamina: {self.player.current_stamina}/{self.player.max_stamina}")


    def attack_enemy(self, enemy_name):
        """Initiates combat with a specified enemy."""
        target_enemy = None
        for enemy in self.current_location.enemies:
            if enemy.is_alive and enemy.name.lower() == enemy_name.lower():
                target_enemy = enemy
                break

        if not target_enemy:
            print(f"No '{enemy_name}' found here.")
            return

        if not self.player.equipped_weapon:
            print("You need to equip a weapon to attack!")
            return

        print(f"\n--- Combat initiated with {target_enemy.name}! ---")
        combat_fled = False # Flag to check if player fled
        while self.player.is_alive and target_enemy.is_alive:
            combat_fled = self.combat_round(target_enemy)
            if combat_fled:
                break # Exit combat loop if player fled
            if not self.player.is_alive:
                self.game_over = True
                print("You have been killed in action. Raid failed!")
                break
            if not target_enemy.is_alive:
                print(f"{target_enemy.name} has been neutralized!")
                self.current_location.remove_enemy(target_enemy)
                self._handle_enemy_loot(target_enemy)
                break
            # Small delay for readability
            time.sleep(1)
        print("--- Combat End ---")


    def combat_round(self, enemy):
        """Handles a single round of combat."""
        # Display exits during combat
        print("\n--- Available Exits ---")
        if not self.current_location.exits:
            print("No immediate exits from this combat zone.")
        else:
            for direction, location in self.current_location.exits.items():
                print(f"- {direction.capitalize()} to {location.name}")
        print("-----------------------")

        # Player's turn
        print("\n--- Your Turn ---")
        action_choice = ""
        # Removed "attack" from valid_combat_choices
        valid_combat_choices = ["head", "body", "flee"] 
        while True:
            player_input = input("Choose your action (head/body/flee)? ").lower().strip()
            
            # Fuzzy match for combat actions
            matching_choices = [choice for choice in valid_combat_choices if choice.startswith(player_input)]

            if len(matching_choices) == 1:
                action_choice = matching_choices[0]
                print(f"(Autocompleted to: {action_choice})")
                break
            elif len(matching_choices) > 1:
                print(f"Ambiguous choice. Did you mean: {', '.join(matching_choices)}?")
            else:
                print("Invalid choice. Please choose 'head', 'body', or 'flee'.") # Updated prompt

        if action_choice == "flee":
            return self._attempt_flee(enemy) # Return True if fled, False if failed

        # If not fleeing, proceed with attack
        player_damage = self.player.damage + random.randint(-5, 5) # Slight variance
        
        base_hit_chance = 0.75 # 75% base hit chance for player
        current_location_range = self.current_location.range_type
        weapon_effective_range = self.player.equipped_weapon.effective_range_type

        # Apply range modifiers to hit chance
        range_modifier = 0
        if current_location_range == "very_short": # Shotguns excel here
            if weapon_effective_range == "very_short": range_modifier += 0.20
            elif weapon_effective_range == "short": range_modifier += 0.10
            elif weapon_effective_range == "medium": range_modifier -= 0.05
            elif weapon_effective_range == "long": range_modifier -= 0.15
        elif current_location_range == "short": # Pistols, SMGs excel here
            if weapon_effective_range == "very_short": range_modifier -= 0.10
            elif weapon_effective_range == "short": range_modifier += 0.15
            elif weapon_effective_range == "medium": range_modifier += 0.05
            elif weapon_effective_range == "long": range_modifier -= 0.10
        elif current_location_range == "medium": # Assault Rifles excel here
            if weapon_effective_range == "very_short": range_modifier -= 0.15
            elif weapon_effective_range == "short": range_modifier -= 0.05
            elif weapon_effective_range == "medium": range_modifier += 0.10
            elif weapon_effective_range == "long": range_modifier += 0.05
        elif current_location_range == "long": # Sniper Rifles excel here
            if weapon_effective_range == "very_short": range_modifier -= 0.30
            elif weapon_effective_range == "short": range_modifier -= 0.20
            elif weapon_effective_range == "medium": range_modifier -= 0.10
            elif weapon_effective_range == "long": range_modifier += 0.20

        final_hit_chance = base_hit_chance + range_modifier
        final_hit_chance = max(0.1, min(0.95, final_hit_chance)) # Cap hit chance between 10% and 95%

        # Determine target part based on action_choice
        target_part = action_choice # Now action_choice is directly "head" or "body"

        actual_hit_location = None # Initialize to None
        
        # Player's attack logic
        player_hit = False
        if target_part == "head":
            headshot_miss_penalty = 0.30
            if random.random() < (final_hit_chance - headshot_miss_penalty):
                # Player hit, now determine if it's a headshot or body shot
                if random.random() < 0.4: # 40% chance to hit head if aimed there AND not an outright miss
                    actual_hit_location = "head"
                    print(f"You aimed for the head and hit the head!")
                else:
                    actual_hit_location = "body"
                    print(f"You aimed for the head but hit the body instead!")
                player_hit = True
            else:
                print(f"You aimed for the head but missed {enemy.name} entirely!")
        else: # Aiming for body
            if random.random() < final_hit_chance:
                actual_hit_location = "body"
                print(f"You aimed for the body and hit the body!")
                player_hit = True
            else:
                print(f"You aimed for the body but missed {enemy.name} entirely!")

        if player_hit:
            player_damage_for_enemy = player_damage
            if actual_hit_location == "head":
                player_damage_for_enemy = int(player_damage_for_enemy * 2) # Double damage for headshot
                print("Critical hit! Headshot!")
            
            actual_damage_dealt = enemy.take_damage(player_damage_for_enemy, hit_location=actual_hit_location) # Pass hit_location to enemy
            print(f"You attack {enemy.name} with your {self.player.equipped_weapon.name}, dealing {actual_damage_dealt} damage.")
            
            # Display enemy condition only if combat is at close range
            if current_location_range == "close":
                print(f"{enemy.name} (Condition: {enemy.get_condition()})")
            else:
                print(f"{enemy.name} is at {current_location_range} range. You can't tell their exact condition.")

            if not enemy.is_alive:
                return False # Enemy defeated, combat ends

        # Enemy's turn - This block now always executes after player's action (hit or miss)
        print("--- Enemy's Turn ---")
        enemy_damage = enemy.damage + random.randint(-3, 3) # Slight variance
        
        # Enemy hit chance based on enemy's base_hit_chance and location range
        enemy_final_hit_chance = enemy.base_hit_chance
        enemy_range_modifier = 0
        
        # Apply range modifiers for enemy hit chance (simplified for enemies)
        if current_location_range == "very_short": enemy_range_modifier += 0.10
        elif current_location_range == "short": enemy_range_modifier += 0.05
        elif current_location_range == "long": enemy_range_modifier -= 0.10 # Harder for enemies to hit at long range

        enemy_final_hit_chance += enemy_range_modifier
        enemy_final_hit_chance = max(0.1, min(0.95, enemy_final_hit_chance))

        # Enemy chooses hit location (randomly)
        enemy_aim_target = random.choice(["head", "body"])
        actual_enemy_hit_location = None

        # Enemy miss chance
        if random.random() > enemy_final_hit_chance:
            print(f"{enemy.name} attacks you but misses!")
            return False # Enemy misses, combat continues

        # If enemy hits, determine specific hit location based on their aim
        if enemy_aim_target == "head":
            if random.random() < 0.3: # 30% chance for enemy to hit head if aiming there
                actual_enemy_hit_location = "head"
                print(f"{enemy.name} aims for your head and hits!")
            else:
                actual_enemy_hit_location = "body"
                print(f"{enemy.name} aims for your head but hits your body instead!")
        else: # Enemy aims for body
            actual_enemy_hit_location = "body"
            print(f"{enemy.name} aims for your body and hits!")

        enemy_damage_to_player = enemy_damage
        if actual_enemy_hit_location == "head":
            enemy_damage_to_player = int(enemy_damage_to_player * 2) # Double damage for headshot
            print("Critical hit! Headshot!")

        actual_damage_taken = self.player.take_damage(enemy_damage_to_player, hit_location=actual_enemy_hit_location) # Pass hit_location to player
        print(f"{enemy.name} attacks you, dealing {actual_damage_taken} damage. Your HP: {self.player.current_health}/{self.player.max_health}")
        self.player.restore_stamina(5) # Passive stamina regen
        return False # Combat continues

    def _attempt_flee(self, enemy):
        """Attempts to flee from combat."""
        print("\n--- Attempting to Flee ---")
        flee_direction = ""
        
        # Fuzzy match for flee direction
        available_exits = list(self.current_location.exits.keys())
        while True:
            flee_input = input(f"Which direction do you want to flee? ({'/'.join(available_exits)}) ").lower().strip()
            matching_directions = [direction for direction in available_exits if direction.startswith(flee_input)]

            if len(matching_directions) == 1:
                flee_direction = matching_directions[0]
                print(f"(Autocompleted to: {flee_direction})")
                break
            elif len(matching_directions) > 1:
                print(f"Ambiguous direction. Did you mean: {', '.join(matching_directions)}?")
            else:
                print("Invalid direction. Please choose an available exit.")

        # Calculate flee chance based on player weight
        # Base flee chance is 80%, reduced by 50% for max weight
        flee_chance = max(0.1, 0.8 - (self.player.get_current_weight() / self.player.max_inventory_weight) * 0.5)
        
        print(f"Your chance to flee: {flee_chance*100:.0f}%")

        if random.random() < flee_chance:
            new_location = self.current_location.exits[flee_direction]
            print(f"You successfully flee {flee_direction} to {new_location.name}!")
            self.current_location = new_location
            self._spawn_random_enemies() # Attempt to spawn enemies in new location
            self.player.restore_stamina(10) # Small stamina restore for fleeing
            self.display_location()
            return True # Fled successfully
        else:
            print("Your escape attempt failed! You couldn't get away.")
            # Enemy gets an immediate extra attack if flee fails
            print(f"--- {enemy.name}'s Counter Attack! ---")
            enemy_damage = enemy.damage + random.randint(-3, 3)
            enemy_final_hit_chance = enemy.base_hit_chance # No range modifier for counter attack
            
            if random.random() < enemy_final_hit_chance:
                hit_location = random.choice(["head", "body"])
                enemy_damage_to_player = enemy_damage
                if hit_location == "head":
                    enemy_damage_to_player = int(enemy_damage_to_player * 2)
                    print("Critical hit! Headshot!")
                actual_damage_taken = self.player.take_damage(enemy_damage_to_player, hit_location=hit_location)
                print(f"{enemy.name} lands a hit on you, dealing {actual_damage_taken} damage. Your HP: {self.player.current_health}/{self.player.max_health}")
            else:
                print(f"{enemy.name} tries to hit you but misses!")
            
            self.player.restore_stamina(5) # Passive stamina regen
            return False # Flee failed, combat continues

    def _handle_enemy_loot(self, enemy):
        """Adds enemy's loot to the current location."""
        print(f"{enemy.name} dropped some loot:")
        
        # Add equipped gear to loot
        if enemy.equipped_weapon:
            self.current_location.add_item(enemy.equipped_weapon)
            print(f"- {enemy.equipped_weapon.name} (equipped weapon)")
        if enemy.equipped_armor:
            self.current_location.add_item(enemy.equipped_armor)
            print(f"- {enemy.equipped_armor.name} (equipped body armor)")
        if enemy.equipped_helmet:
            self.current_location.add_item(enemy.equipped_helmet)
            print(f"- {enemy.equipped_helmet.name} (equipped helmet)")

        # Add other loot items
        if enemy.loot_items:
            for item in enemy.loot_items:
                self.current_location.add_item(item)
                print(f"- {item.name}")
        
        if not enemy.equipped_weapon and not enemy.equipped_armor and not enemy.equipped_helmet and not enemy.loot_items:
            print(f"{enemy.name} dropped nothing of value.")

    def check_extraction(self):
        """Checks if the player is at an extraction point and can extract."""
        if self.current_location.is_extraction_point:
            if not self.current_location.enemies:
                print(f"You have successfully extracted from {self.current_location.name}! Raid complete!")
                self.game_won = True
                self.game_over = True
            else:
                print("You cannot extract while enemies are present! Clear the area first.")
        else:
            print("This is not an extraction point. Find a designated extraction zone.")

    def run(self):
        """Main game loop."""
        print("Welcome to Escape from Tarkov: Text-Based MUD!")
        print("Type 'help' for a list of commands.")
        self.display_location()

        while not self.game_over:
            print(f"\n--- Raid Timer: {self.raid_timer} actions remaining ---") # Display timer
            command = input("\nWhat do you do, PMC? ").strip()
            if command:
                self.handle_input(command)
            else:
                print("Please enter a command.")

            if self.player.current_health <= 0:
                self.game_over = True
                print("\nYour health has dropped to zero. You are KIA. Raid failed!")

            # Small delay to make it feel less instant
            time.sleep(0.5)

        if self.game_won:
            print("\nCongratulations, PMC! You survived the raid!")
        else:
            print("\nGame Over. Better luck next time.")

if __name__ == "__main__":
    game = Game()
    game.run()
