from django.db import migrations

def cleanup_state_data(apps, schema_editor):
    Provider = apps.get_model('patient_records', 'Provider')
    # Map of full state names to abbreviations
    state_map = {
        'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
        'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
        'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA',
        'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD',
        'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS',
        'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV',
        'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY',
        'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
        'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
        'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
        'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI',
        'WYOMING': 'WY', 'DISTRICT OF COLUMBIA': 'DC'
    }
    
    for provider in Provider.objects.all():
        state = provider.state.upper() if provider.state else ''
        # If it's already a valid 2-letter code, keep it
        if len(state) == 2 and state.isalpha():
            provider.state = state
        # Otherwise try to map it
        else:
            provider.state = state_map.get(state, 'XX')  # Default to 'XX' if unknown
        provider.save()

class Migration(migrations.Migration):
    dependencies = [
        ('patient_records', '0002_alter_eventstore_options_and_more'),
    ]

    operations = [
        migrations.RunPython(cleanup_state_data),
    ] 