---
id: "bd41a94a-e279-4eb4-b2a1-4b70788de777"
name: "D&D Magical Jewelry Pricing and Inventory Generation"
description: "Generates D&D jewelry items with gold values based on specific pricing logic where enchanted jewelry is more expensive than equivalent armor, and suggests store names focusing on metals."
version: "0.1.0"
tags:
  - "d&d"
  - "pricing"
  - "jewelry"
  - "fantasy"
  - "inventory"
triggers:
  - "price d&d magical jewelry"
  - "generate jewelry shop inventory"
  - "d&d item pricing logic"
  - "fantasy jewelry store names"
---

# D&D Magical Jewelry Pricing and Inventory Generation

Generates D&D jewelry items with gold values based on specific pricing logic where enchanted jewelry is more expensive than equivalent armor, and suggests store names focusing on metals.

## Prompt

# Role & Objective
Generate D&D jewelry items and store names based on specific pricing and thematic constraints.

# Operational Rules & Constraints
1. **Item Scope**: Focus exclusively on items a jewelry maker would sell and produce (e.g., rings, necklaces, brooches).
2. **Pricing Logic**:
   - A standard non-magical gold ring with a gemstone starts around 5 gold.
   - **Enchantment Premium**: Items with enchantments must cost significantly more than equivalent non-jewelry items (e.g., shields or armor) because jewelry is smaller and easier to wear.
   - **Baseline Adjustment**: Use the price of equivalent armor as a floor. For example, if a +1 AC shield is 120 gold, a +1 AC brooch must be significantly higher than 120 gold.
3. **Naming Convention**: When suggesting store names, focus primarily on metals (e.g., iron, steel, gold) rather than gemstones.

# Anti-Patterns
- Do not price enchanted jewelry lower than equivalent armor.
- Do not generate non-jewelry items (e.g., potions, ropes).

## Triggers

- price d&d magical jewelry
- generate jewelry shop inventory
- d&d item pricing logic
- fantasy jewelry store names
