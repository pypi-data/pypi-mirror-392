# conflictid

A general-purpose deconfliction engine as a reusable Django app.

`smoothglue_conflictid` provides a fast, database-backed engine for detecting temporal (time/date) and resource (string) conflicts.

It is built using a **"Synchronized Index Table"** pattern. Instead of running slow, in-memory Python loops, you sync your application's models to a generic, indexed ConflictItem table. This allows the library to use fast, database-native queries (via GiST indexes) to find potential conflicts in sub-second time. This is useful for scheduling or planning applications that wish to alert users to potential resource conflicts prior to allocation.

## Key Features

- **High-Performance:** Uses PostgreSQL GiST indexes for sub-second range overlap queries.

- **Synchronous API:** Provides a synchronous API endpoint for checking conflicts against indexed items, eliminating race conditions and returning an immediate response.

- **Reliable Sync:** Includes helper functions (sync_item, sync_items_bulk) to keep your models synchronized with the conflict index, even during bulk operations.

- **General-Purpose:** Designed to handle any conflict based on:

  - **Resource:** (e.g., "HMMWV-123", "Room 201")

  - **Time:** (e.g., `2025-12-01T09:00Z` to `2025-12-01T10:00Z`)

  - **Integer Range:** (e.g., Altitude 10,000 to 15,000)

## Installation (for Host Apps)

1. Install the package:

```bash
pip install smoothglue_conflictid
```

2. Add to your Django `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django.contrib.postgres", # Required for range fields
    "rest_framework",
    # Add the namespaced library app
    "smoothglue.conflictid",
    ...
    "your_app", # Your application
]
```

3. Run migrations to create the `ConflictItem` table and enable extensions:

```python
python manage.py migrate conflictid
```

## Host App Integration Guide

To use `smoothglue_conflictid`, you must do two things:

1. Sync Data: Keep the `ConflictItem` shadow table in sync with your native models.

2. Expose API: Create an API endpoint that uses the library's query builder to check for conflicts; referred to as "deconfliction" in this guide.

This guide uses a "scheduling_app" with an `Equipment` and `Reservation` model as an example.

1. Sync: `models.py`

You must override the `save()` and `delete()` methods on your "conflict-able" model (e.g., `Reservation`) to sync its data with conflictid.

```python
# in your_app/models.py
from django.db import models
from smoothglue.conflictid.sync import sync_item
from .managers import ReservationManager # We will create this next

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Attach a custom manager for bulk operations
    objects = ReservationManager()

    def to_conflict_item_dict(self):
        """
        Helper method to format this model's data for the
        conflictid library.
        """
        return {
            "source_app": "scheduling_app", # Your app's name
            "source_object_id": str(self.id),
            "resource_id": str(self.equipment.serial_number),
            "temporal_range": (self.start_time, self.end_time),
            "integer_range": None, # (or e.g., (self.min_alt, self.max_alt))
        }

    def save(self, *args, **kwargs):
        """
        Override save() to explicitly call the conflictid sync helper.
        """
        super().save(*args, **kwargs) # Save the real object first
        sync_item(self.to_conflict_item_dict()) # Sync to shadow table

    def delete(self, *args, **kwargs):
        """
        Override delete() to explicitly call the conflictid sync helper.
        """
        # Sync *before* deleting, while we still have the data
        sync_item(self.to_conflict_item_dict(), delete=True)
        super().delete(*args, **kwargs) # Now delete the real object

```

2. Sync: `managers.py` (Handling Bulk Operations)

Standard `.save()` and `.delete()` methods are bypassed by bulk operations (`bulk_create`, `bulk_update`, `queryset.delete()`). If your app uses these (e.g., for data importers), you must override the manager to keep the shadow table in sync.

```python
# in your_app/managers.py
from django.db import models
from smoothglue.conflictid.sync import sync_items_bulk

class ReservationManager(models.Manager):

    def bulk_create(self, reservations, **kwargs):
        """
        Override bulk_create to explicitly call the sync helper.
        """
        # 1. Create the real objects
        created_reservations = super().bulk_create(reservations, **kwargs)

        # 2. Format the data for the conflict library
        conflict_data = [
            res.to_conflict_item_dict() for res in created_reservations
        ]

        # 3. Call the library's bulk sync helper
        if conflict_data:
            sync_items_bulk(conflict_data)

        return created_reservations

    # NOTE: A complete implementation would also override
    # bulk_update() and queryset.delete()
```

3. API: `serializers.py`

You need two serializers: one for your native model (`ReservationSerializer`) and one to validate data for the conflict check API (`DeconflictionCheckSerializer`).

```python
# in your_app/serializers.py
from rest_framework import serializers
from .models import Equipment, Reservation

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = '__all__'

class DeconflictionCheckSerializer(serializers.Serializer):
    """
    Serializer for the "deconfliction" API. It validates the *proposed*
    data from the client.
    """
    id = serializers.IntegerField(required=False, help_text="The ID of the item being edited (if any).")
    equipment_serial = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
```

4. API: views.py

Expose a view for your native model (`ReservationViewSet`) and, most importantly, the `DeconflictionCheckView`. This view uses the conflictid.queries.DeconflictionQuery builder to find conflicts.

```python
# in your_app/views.py
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer, DeconflictionCheckSerializer
from smoothglue.conflictid.queries import DeconflictionQuery
from smoothglue.conflictid.serializers import ConflictItemSerializer # From the library

class ReservationViewSet(viewsets.ModelViewSet):
    """
    API for your native Reservation model.
    POSTing here will trigger the .save() and sync logic.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

class DeconflictionCheckView(views.APIView):
    """
    This is the API for checking conflicts.

    It accepts a *proposed* reservation and returns any
    conflicts without saving the reservation.
    """
    def post(self, request, *args, **kwargs):
        serializer = DeconflictionCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 1. Build the query from the proposed data
        query = (
            DeconflictionQuery()
            .with_resource_id(data["equipment_serial"])
            .with_temporal_overlap(data["start_time"], data["end_time"])
            .exclude_self(
                source_app="scheduling_app", # Your app's name
                source_object_id=str(data.get("id")) # None for new items
            )
        )

        # 2. Execute the fast, indexed query
        conflicts = query.execute()

        # 3. Return the list of conflicts immediately
        conflict_serializer = ConflictItemSerializer(conflicts, many=True)
        return Response(conflict_serializer.data, status=status.HTTP_200_OK)

```

5. API: `urls.py`

Finally, hook up your views to your project's URL configuration.

```python
# in your_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet, DeconflictionCheckView

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('deconfliction/check/', DeconflictionCheckView.as_view(), name='deconfliction-check'),
]

# --- Then, in your main project's config/urls.py ---
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/scheduling/', include('scheduling_app.urls')),
# ]
```

## Example API Interaction

With this setup, your host app is now deconfliction-aware.

1. Create a "Blocker" Reservation:
   `POST /api/scheduling/reservations/`

```
{
    "equipment": 1,
    "start_time": "2025-12-01T09:00:00Z",
    "end_time": "2025-12-01T10:00:00Z"
}
```

This creates a `Reservation` and syncs it to `ConflictItem`.

2. Check for a Conflict (deconfliction):
   `POST /api/scheduling/deconfliction/check/`

```python
{
    "equipment_serial": "HMMWV-123",
    "start_time": "2025-12-01T09:30:00Z",
    "end_time": "2025-12-01T10:30:00Z"
}
```

3. Response (Conflict Found):
   The API returns the full `ConflictItem` of the "blocker" reservation.

```JSON
[
    {
        "id": 1,
        "resource_id": "HMMWV-123",
        "temporal_range": {
            "lower": "2025-12-01T09:00:00+00:00",
            "upper": "2025-12-01T10:00:00+00:00",
            "bounds": {
                "lower_inclusive": true,
                "upper_inclusive": false
            }
        },
        "integer_range": null,
        "arbitrary_dims": null,
        "source_app": "scheduling_app",
        "source_object_id": "1"
    }
]
```

4. Response (No Conflict):
   If you check for a different time or resource, the API returns an empty list.

```JSON
[]
```

## Local Development (Docker)

This is the recommended way to run the sandbox for development. It ensures a consistent environment and automatically runs migrations on startup.

1. Copy the environment file:

```
cp sandbox/.env.example sandbox/config/.env
```

2. Build and run the containers:

```
docker-compose -f sandbox/docker-compose.yml up --build
```

The server will be available at `http://localhost:8000`
Any changes you make to the code (in either the `conflictid` library or the `sandbox` app) will cause the Django server to automatically reload.

## Running Tests

Docker (Recommended):

Run the `pytest` command inside the running web container:

```bin/bash
docker-compose -f sandbox/docker-compose.yml exec web pytest
```

Local Virtual Environment:

If you are running the sandbox locally with a virtual environment:

1. Ensure your virtual environment is active.

2. Run `pytest` from the root directory:

```bin/bash
pytest conflictid/
```

## Local Development (Virtual Environment)

You can also run the sandbox locally using a Python virtual environment.

1. Create a virtual environment and install the library in "editable" mode with its dev dependencies:

```bin/bash
python -m venv .venv
source .venv/bin/activate

# This one command installs Django, DRF, psycopg2, and pytest
pip install -e ".[dev]"
```

2. Set up PostgreSQL: Ensure you have a local PostgreSQL server running. Create a database named `conflictid_db` with a user/password postgres/password (or update `sandbox/sandbox/settings.py` to match your credentials).
   Run the sandbox:

```bash
cd sandbox
python manage.py migrate
python manage.py runserver
```
