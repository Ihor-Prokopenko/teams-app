from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


class ListMixin:
    """ Add pagination to the list """
    def list(self: Request, request, *args, **kwargs) -> Response:
        """ Add pagination to the list """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                "pages": (queryset.count() + self.pagination_class.page_size - 1) // self.pagination_class.page_size,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
