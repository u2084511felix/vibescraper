import json
import os


def save_page_json(page_url, page_summary, top_results, output_dir='./results'):
    """Save page results to a JSON file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create filename from URL
    filename = page_url.replace('://', '_').replace('/', '_').replace('.', '_')
    filepath = os.path.join(output_dir, f"{filename}.json")

    # Create JSON data
    data = {
        'url': page_url,
        'page_summary': page_summary,
        'chunks': []
    }

    if top_results:
        for i, result in enumerate(top_results):
            data['chunks'].append({
                'rank': i+1,
                'chunk_text': result['chunk_text'],
                'similarity': float(result['similarity']),
            })

        # Write to JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return filepath
    return None


def save_combined_json(search_query, combined_summary, pages_data, filepath=None):
    """Save combined results to a JSON file"""
    # Generate filepath if not provided
    if not filepath:
        output_dir = './results'
        os.makedirs(output_dir, exist_ok=True)
        filename = search_query.replace(' ', '_').replace(
            '?', '').replace('/', '_')[:50]
        filepath = os.path.join(output_dir, f"{filename}_combined.json")
    else:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Create data structure
    data = {
        'combined_summary': combined_summary,
        'pages': pages_data
    }

    # Write to JSON file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
    return filepath
