from rest_framework import serializers

from .models import Bookmark, Collection


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'title', 'description', 'url', 'bookmark_type', 'collections']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'description']


class BookmarkRequestSerializer(serializers.ModelSerializer):
    collections = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), many=True, required=False)

    class Meta:
        model = Bookmark
        fields = ['url', 'collections']

    def create(self, validated_data):
        from .views import check_og_type, get_open_graph_data
        url = validated_data.get('url')
        collections = validated_data.get('collections', [])
        og_data = get_open_graph_data(url)

        if og_data:
            validated_data['title'] = og_data.get('title', '')
            validated_data['description'] = og_data.get('description', '')
            validated_data['preview_image'] = og_data.get('image', '')
            validated_data['bookmark_type'] = check_og_type(og_data.get('type', ''))
            validated_data['url'] = url

        collections = validated_data.pop('collections', [])  # Удаляем 'collections' из validated_data
        bookmark = Bookmark.objects.create(**validated_data)
        bookmark.collections.set(collections)
        return bookmark


class CollectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['title', 'description']

    def create(self, validated_data):
        collection = Collection.objects.create(**validated_data)
        return collection
