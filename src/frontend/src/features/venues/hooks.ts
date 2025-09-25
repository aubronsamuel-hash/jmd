import { useQuery } from "@tanstack/react-query";

import { useApi } from "@/features/shared/api-provider";

const venuesKeys = {
  all: ["venues"] as const,
  list: () => [...venuesKeys.all, "list"] as const,
};

export function useVenues() {
  const { venues } = useApi();
  return useQuery({
    queryKey: venuesKeys.list(),
    queryFn: () => venues.list(),
  });
}
