import pytest


def test_apple_charlotte_recipe():
    ingredients = {
        0: "sunflower oil",
        1: "3 cups peeled and diced apples",
        2: "1 lime, juiced",
        3: "¾ cup all-purpose flour",
        4: "½ teaspoon ground cinnamon",
        5: "½ teaspoon ground ginger",
        6: "¼ teaspoon salt",
        7: "2 large eggs",
        8: "½ cup brown sugar",
        9: "¼ cup white sugar",
        10: "1 teaspoon vanilla extract",
    }

    recipe_lines = {
        "Step 1": "Preheat the oven to 350 degrees F (175 degrees C). Pour a 6½-inch springform pan with sunflower oil and line with parchment paper. Pour parchment paper with sunflower oil.",
        "Step 2": "Toss apples with lime juice and set aside. Mix flour, cinnamon, ginger, and salt in a bowl and set aside.",
        "Step 3": "Combine eggs with brown sugar, white sugar, and vanilla extract in a second bowl and beat with an electric mixer until creamy. Add dry ingredients and mix until just combined. Pour about 1/3 of the batter into the prepared pan. Add apples and top with remaining batter.",
        "Step 4": "Bake in the preheated oven until a toothpick inserted in center comes out clean, 50 to 60 minutes. Transfer to a wire rack and cool for 15 minutes.",
        "Step 5": "Run a knife around the springform pan, release springform, and flip apple Charlotte onto a plate. Immediately flip the cake onto a serving platter.",
    }

    print("\nIngredients:")
    for num, ingredient in ingredients.items():
        print(f"{num}: {ingredient}")

    print("\nActions:")
    for step, line in recipe_lines.items():
        print(f"{step}: {line}")

    assert True == True
