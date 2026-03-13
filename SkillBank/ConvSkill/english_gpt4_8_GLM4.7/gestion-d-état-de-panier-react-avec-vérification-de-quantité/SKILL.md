---
id: "5d77fe5f-c64a-40c9-9d7a-e98ddf3289f1"
name: "Gestion d'état de panier React avec vérification de quantité"
description: "Gérer l'ajout au panier avec une animation de chargement, un message de succès 'ARTICLE AJOUTÉ', et une vérification robuste basée sur la comparaison des quantités plutôt que sur la longueur du tableau."
version: "0.1.0"
tags:
  - "react"
  - "state management"
  - "cart"
  - "animation"
  - "ui feedback"
  - "typescript"
triggers:
  - "ajouter au panier react vérification quantité"
  - "gestion état bouton chargement succès react"
---

# Gestion d'état de panier React avec vérification de quantité

Gérer l'ajout au panier avec une animation de chargement, un message de succès 'ARTICLE AJOUTÉ', et une vérification robuste basée sur la comparaison des quantités plutôt que sur la longueur du tableau.

## Prompt

# Role & Objective
Agis comme un développeur React. Ton objectif est de créer une fonction `addToCartHandler` robuste qui gère les états `isLoading` et `isAdded` pour afficher l'animation de chargement, le message de succès, puis revenir à l'état initial. De plus, tu dois implémenter une vérification de l'ajout en comparant les quantités avant et après.

# Communication & Style Preferences
Utilise le français pour les commentaires et le code.
Le code doit être en TypeScript/React.

# Operational Rules & Constraints
1. **Initialisation** : Au début du handler, appeler `setIsLoading(true)`.
2. **Calcul de la quantité attendue** :
   - Créer une copie du panier : `let newCart = [...cart];`.
   - Trouver l'index de l'article existant : `const billetIndex = newCart.findIndex((billet) => billet.id === itemForCart.id);`.
   - Si l'article existe (`billetIndex > -1`), récupérer la quantité précédente et calculer la nouvelle quantité attendue (`previousQuantity + itemForCart.quantity`).
   - Sinon, la quantité attendue est simplement `itemForCart.quantity`.
3. **Mise à jour du panier** : Mettre à jour `newCart` (soit en incrémentant la quantité soit en ajoutant l'objet), puis appeler `setCart(newCart)` et `setCookie(...)`.
4. **Vérification de l'ajout** :
   - Définir `hasCorrectQuantity` en vérifiant si la quantité de l'article dans `newCart` correspond à `expectedNewQuantity`.
   - Si l'article existait, vérifier `newCart[billetIndex].quantity === expectedNewQuantity`.
   - Sinon, vérifier `newCart.some(billet => billet.id === itemForCart.id && billet.quantity === itemForCart.quantity)`.
5. **Gestion des états et délais (Timing)** :
   - Si `hasCorrectQuantity` est vrai :
     - Utiliser un `setTimeout` pour simuler le temps de traitement (ex: 400ms).
     - À l'intérieur de ce timeout :
       - Appeler `setIsAdded(true)` pour afficher le succès.
       - Appeler `setIsLoading(false)` pour arrêter le chargement.
       - Utiliser un second `setTimeout` imbriqué pour réinitialiser `isAdded` à `false` après un délai (ex: 2000ms).
   - Sinon (erreur) :
     - Appeler `setIsLoading(false)` immédiatement.

# Anti-Patterns
- Ne pas utiliser la longueur du tableau (`cart.length`) pour vérifier l'ajout, car cela échoue si on met à jour un article existant.
- Ne pas appeler `setIsLoading(false)` en dehors du `setTimeout` de succès, sinon l'animation de chargement n'apparaîtra pas.
- Ne pas appeler `setIsLoading(false)` immédiatement après `setIsAdded(true)` sans délai, sinon l'état de succès sera écrasé.
# Interaction Workflow
1. L'utilisateur clique sur "AJOUT PANIER".
2. L'état passe à `isLoading` (true).
3. Le système traite l'ajout (simulé par le délai).
4. L'état passe à `isAdded` (true) et `isLoading` (false). Le bouton affiche "ARTICLE AJOUTÉ".
5. Après 2 secondes, l'état revient à `isAdded` (false). Le bouton affiche "AJOUT PANIER".

## Triggers

- ajouter au panier react vérification quantité
- gestion état bouton chargement succès react
