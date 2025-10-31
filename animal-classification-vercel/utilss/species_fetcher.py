import requests


# utilss/species_fetcher.py

def fetch_species_names(predicted_class, top_n=3):
    predicted_class = predicted_class.lower().replace("_", " ")

    breed_map = {
        "bear": ["Grizzly Bear", "Sun Bear", "Sloth Bear", "Polar Bear", "Asiatic Black Bear", "American Black Bear"],
        "cat": ["Persian Cat", "Siamese Cat", "Maine Coon", "Bengal Cat"],
        "dog": ["Golden Retriever", "Labrador", "German Shepherd", "Pug"],
        "elephant": ["African Elephant", "Asian Elephant"],
        "deer": ["White-tailed Deer", "Mule Deer", "Red Deer"],
        "bird": ["Sparrow", "Parrot", "Peacock", "Crow"],
        "cow": ["Jersey Cow", "Holstein", "Angus"],
        "dolphin": ["Bottlenose Dolphin", "Spinner Dolphin"],
        "giraffe": ["Masai Giraffe", "Reticulated Giraffe"],
        "horse": ["Arabian Horse", "Thoroughbred", "Clydesdale"],
        "kangaroo": ["Red Kangaroo", "Eastern Grey Kangaroo"],
        "lion": ["African Lion", "Asiatic Lion"],
        "panda": ["Giant Panda", "Red Panda"],
        "tiger": ["Bengal Tiger", "Siberian Tiger"],
        "zebra": ["Mountain Zebra", "Plains Zebra"]
    }

    for key in breed_map:
        if key in predicted_class:
            return breed_map[key][:top_n]

    # Fallback if no match
    return [predicted_class.title()]
