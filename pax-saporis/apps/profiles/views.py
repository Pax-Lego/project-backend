from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.profiles.models import UserProfile, WeightEntry
from apps.profiles.serializers import UserProfileSerializer, WeightEntrySerializer


class ProfileView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)

    def partial_update(self, request, pk=None):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WeightEntryViewSet(viewsets.ModelViewSet):
    serializer_class = WeightEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return WeightEntry.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)
