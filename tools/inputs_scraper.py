import os
import json
from selenium.webdriver.common.by import By

def inputs_scraper(driver, section_name, output_dir="Main/data/vintrace_reports/"):
    """
    Scrapes input fields (dropdowns, text boxes, etc.) from the current report section and saves their metadata to a JSON file.

    Args:
        driver: Selenium WebDriver instance, already navigated to the desired report section.
        section_name: String name of the report section (used for JSON file naming).
        output_dir: Directory to save the JSON file (created automatically if missing).
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    inputs_map = {}

    # Find all inputs, selects, and textareas visible in the section
    input_elements = driver.find_elements(By.XPATH, "//input|//select|//textarea")

    for elem in input_elements:
        input_info = {}
        input_info['id'] = elem.get_attribute('id')
        input_info['name'] = elem.get_attribute('name')
        input_info['type'] = elem.tag_name
        input_info['class'] = elem.get_attribute('class')

        # Try to find the label text
        label = None
        if input_info['id']:
            label_elems = driver.find_elements(By.XPATH, f"//label[@for='{input_info['id']}']")
            if label_elems:
                label = label_elems[0].text
        if not label:
            try:
                parent = elem.find_element(By.XPATH, "..")
                if parent.tag_name == 'label':
                    label = parent.text
                elif parent.text.strip():
                    label = parent.text.strip()
            except Exception:
                label = None  # parent might not exist
        input_info['label'] = label

        # For selects, get options
        if elem.tag_name == 'select':
            options = []
            for opt in elem.find_elements(By.TAG_NAME, "option"):
                options.append({"value": opt.get_attribute("value"), "text": opt.text})
            input_info['options'] = options

        # Use id, name, or fallback key
        key = input_info['id'] or input_info['name'] or f"{elem.tag_name}_{len(inputs_map)}"
        inputs_map[key] = input_info

    # Save to JSON
    safe_section_name = section_name.replace(" ", "_")
    output_path = os.path.join(output_dir, f"{safe_section_name}_section_map.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inputs_map, f, indent=4, ensure_ascii=False)

    print(f"Input map for '{section_name}' saved to {output_path}")