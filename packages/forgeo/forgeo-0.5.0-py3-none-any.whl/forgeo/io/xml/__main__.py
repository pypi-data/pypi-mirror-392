from forgeo.io.xml import _collect_serializers as collect_serializers

print("Available XML serializers:")
for serializer in collect_serializers():
    print(f" - {serializer.tag}: {serializer.target}")
