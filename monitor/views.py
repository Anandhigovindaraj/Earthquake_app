import requests
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import pytz  

def index(request):
    """
    Render the main webpage.
    """
    return render(request, 'index.html')

def earthquake_data(request):
    """
    API endpoint to fetch earthquake data from USGS for a specific date or date range (last 10 years) in GeoJSON format.
    """
    # Get the date or date range parameters from the request
    date_param = request.GET.get('date')  # Corrected: Use only the key
    start_date_param = request.GET.get('start_date')  # Corrected: Use only the key
    end_date_param = request.GET.get('end_date')  # Corrected: Use only the key

    # Check if specific date is provided
    if date_param:
        try:
            selected_date = datetime.strptime(date_param, '%Y-%m-%d')
            # Set the time to the start of the day (UTC)
            selected_date = selected_date.replace(tzinfo=pytz.UTC)
            start_of_day = selected_date
            end_of_day = selected_date + timedelta(days=1)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
    # Check if start and end date range are provided
    elif start_date_param and end_date_param:
        try:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').replace(tzinfo=pytz.UTC) + timedelta(days=1)  # Include the end date
            start_of_day = start_date
            end_of_day = end_date
        except ValueError:
            return JsonResponse({'error': 'Invalid date range format. Use YYYY-MM-DD for both dates.'}, status=400)
    # If no date or range is provided, default to the last 10 years
    else:
        end_of_day = datetime.now(pytz.UTC)  # Get current time in UTC
        start_of_day = end_of_day - timedelta(days=365*10)  # 10 years ago

    try:
        # Construct the URL for the USGS Earthquake API with the calculated or provided date range
        url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?starttime={start_of_day.strftime("%Y-%m-%dT%H:%M:%SZ")}&endtime={end_of_day.strftime("%Y-%m-%dT%H:%M:%SZ")}&format=geojson'

        # Fetch earthquake data from the USGS API
        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse({'error': f'Error fetching data from USGS: {response.status_code}'}, status=500)

        data = response.json()

        # Check if features exist in the data
        if 'features' not in data or not data['features']:
            return JsonResponse({'message': 'No earthquake data found for the specified date or date range.'}, status=404)

        # Return the GeoJSON response directly from USGS
        return JsonResponse(data)

    except Exception as e:
        # Catch unexpected errors and log them
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)
