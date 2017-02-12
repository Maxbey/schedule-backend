from rest_framework import serializers

from ..models import Specialty, Troop, Discipline, Theme


class TroopSerializer(serializers.ModelSerializer):
    code = serializers.CharField()
    day = serializers.ChoiceField(Troop.DAY_CHOICES)
    term = serializers.IntegerField()

    specialty = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects
    )
    specialty_code = serializers.CharField(
        read_only=True, source='specialty.code'
    )

    class Meta:
        model = Troop
        exclude = [
            'created_at',
            'updated_at'
        ]


class SpecialtySerializer(serializers.ModelSerializer):
    code = serializers.CharField()

    troops = TroopSerializer(read_only=True, many=True)
    disciplines = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects, many=True
    )

    class Meta:
        model = Specialty
        exclude = [
            'created_at',
            'updated_at'
        ]


class ThemeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    number = serializers.CharField()
    term = serializers.IntegerField()
    self_education = serializers.BooleanField()
    duration = serializers.ChoiceField(Theme.DURATION_CHOICES)

    audiences_count = serializers.IntegerField()
    teachers_count = serializers.IntegerField()

    discipline = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects
    )
    previous_themes = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects, many=True
    )

    class Meta:
        model = Theme
        exclude = [
            'created_at',
            'updated_at'
        ]


class DisciplineSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    short_name = serializers.CharField()

    specialties = serializers.PrimaryKeyRelatedField(
        queryset=Specialty.objects, many=True
    )
    themes = ThemeSerializer(read_only=True, many=True)

    class Meta:
        model = Discipline
        exclude = [
            'created_at',
            'updated_at'
        ]
