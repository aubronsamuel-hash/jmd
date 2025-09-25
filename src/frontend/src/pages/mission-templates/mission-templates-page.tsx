import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { useMissionTags } from "@/features/mission-tags/hooks";
import {
  useCreateMissionTemplate,
  useMissionTemplates,
  useUpdateMissionTemplate,
} from "@/features/mission-templates/hooks";
import { useVenues } from "@/features/venues/hooks";
import type { MissionTemplateCreate } from "@/lib/api/types";

const initialTemplate: MissionTemplateCreate = {
  name: "",
  description: "",
  teamSize: 1,
  requiredSkills: [],
  defaultStartTime: "",
  defaultEndTime: "",
  defaultVenueId: undefined,
  tagIds: [],
};

export function MissionTemplatesPage(): JSX.Element {
  const { data: templates, isLoading, isError, error } = useMissionTemplates();
  const { data: venues } = useVenues();
  const { data: tags } = useMissionTags();
  const createTemplate = useCreateMissionTemplate();
  const [formState, setFormState] = useState<MissionTemplateCreate>(initialTemplate);

  const sortedTemplates = useMemo(
    () => (templates ?? []).slice().sort((a, b) => a.name.localeCompare(b.name)),
    [templates],
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!formState.name.trim()) {
      return;
    }
    try {
      await createTemplate.mutateAsync({
        ...formState,
        teamSize: Number(formState.teamSize) || 1,
        requiredSkills: formState.requiredSkills.filter(Boolean),
        defaultStartTime: formState.defaultStartTime || undefined,
        defaultEndTime: formState.defaultEndTime || undefined,
        defaultVenueId: formState.defaultVenueId || undefined,
      });
    } catch (error) {
      // Les erreurs sont exposées via createTemplate.isError.
    } finally {
      setFormState(initialTemplate);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-2xl">Gabarits de mission</CardTitle>
          <CardDescription>
            Organisez vos besoins récurrents et préparez des missions prêtes à planifier.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col gap-4" aria-busy>
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : isError ? (
            <div
              role="alert"
              className="rounded-md border border-destructive bg-destructive/10 p-4 text-sm"
            >
              Impossible de charger les gabarits :{" "}
              {error instanceof Error ? error.message : "erreur inconnue"}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nom</TableHead>
                    <TableHead>Équipe</TableHead>
                    <TableHead>Horaires</TableHead>
                    <TableHead>Tags</TableHead>
                    <TableHead>Salle par défaut</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedTemplates.map((template) => (
                    <MissionTemplateRow key={template.id} templateId={template.id} />
                  ))}
                  {sortedTemplates.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Aucun gabarit enregistré.
                      </TableCell>
                    </TableRow>
                  ) : null}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Créer un gabarit</CardTitle>
          <CardDescription>Définissez une mission type pour vos équipes.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="template-name">Nom</Label>
              <Input
                id="template-name"
                required
                value={formState.name}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, name: event.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="template-description">Description</Label>
              <Textarea
                id="template-description"
                value={formState.description ?? ""}
                onChange={(event) =>
                  setFormState((state) => ({ ...state, description: event.target.value }))
                }
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="template-team-size">Taille d&apos;équipe</Label>
                <Input
                  id="template-team-size"
                  type="number"
                  min={1}
                  value={formState.teamSize}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, teamSize: Number(event.target.value) }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-skills">Compétences (séparées par des virgules)</Label>
                <Input
                  id="template-skills"
                  value={formState.requiredSkills.join(", ")}
                  onChange={(event) =>
                    setFormState((state) => ({
                      ...state,
                      requiredSkills: event.target.value
                        .split(",")
                        .map((skill) => skill.trim())
                        .filter(Boolean),
                    }))
                  }
                />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="template-start">Heure de début</Label>
                <Input
                  id="template-start"
                  type="time"
                  value={formState.defaultStartTime ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, defaultStartTime: event.target.value }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-end">Heure de fin</Label>
                <Input
                  id="template-end"
                  type="time"
                  value={formState.defaultEndTime ?? ""}
                  onChange={(event) =>
                    setFormState((state) => ({ ...state, defaultEndTime: event.target.value }))
                  }
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="template-venue">Salle par défaut</Label>
              <select
                id="template-venue"
                className="w-full rounded-md border border-input bg-background p-2 text-sm"
                value={formState.defaultVenueId ?? ""}
                onChange={(event) =>
                  setFormState((state) => ({
                    ...state,
                    defaultVenueId: event.target.value || undefined,
                  }))
                }
              >
                <option value="">Aucune</option>
                {(venues ?? []).map((venue) => (
                  <option key={venue.id} value={venue.id}>
                    {venue.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="template-tags">Tags</Label>
              <select
                id="template-tags"
                multiple
                className="h-32 w-full rounded-md border border-input bg-background p-3 text-sm"
                value={formState.tagIds}
                onChange={(event) => {
                  const options = Array.from(event.target.selectedOptions).map(
                    (option) => option.value,
                  );
                  setFormState((state) => ({ ...state, tagIds: options }));
                }}
              >
                {(tags ?? []).map((tag) => (
                  <option key={tag.id} value={tag.id}>
                    {tag.label}
                  </option>
                ))}
              </select>
            </div>
            <Button type="submit" className="w-full" disabled={createTemplate.isPending}>
              {createTemplate.isPending ? "Création en cours..." : "Créer"}
            </Button>
            {createTemplate.isError ? (
              <p role="alert" className="text-sm text-destructive">
                Impossible d&apos;enregistrer le gabarit :{" "}
                {createTemplate.error instanceof Error
                  ? createTemplate.error.message
                  : "erreur inconnue"}
              </p>
            ) : null}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function MissionTemplateRow({ templateId }: { templateId: string }) {
  const { data: templates } = useMissionTemplates();
  const template = templates?.find((item) => item.id === templateId);
  const updateTemplate = useUpdateMissionTemplate(templateId);
  const [isExpanded, setExpanded] = useState(false);

  if (!template) {
    return null;
  }

  return (
    <TableRow className="align-top">
      <TableCell className="space-y-2">
        <div className="font-medium">{template.name}</div>
        {template.description ? (
          <p className="text-xs text-muted-foreground">{template.description}</p>
        ) : null}
        <Button variant="ghost" size="sm" onClick={() => setExpanded((value) => !value)}>
          {isExpanded ? "Masquer" : "Éditer"}
        </Button>
        {isExpanded ? (
          <InlineTemplateEditor templateId={templateId} onClose={() => setExpanded(false)} />
        ) : null}
      </TableCell>
      <TableCell>
        <span className="font-medium">{template.teamSize} pers.</span>
        {template.requiredSkills.length ? (
          <div className="mt-1 text-xs text-muted-foreground">
            {template.requiredSkills.join(", ")}
          </div>
        ) : null}
      </TableCell>
      <TableCell>
        {template.defaultStartTime && template.defaultEndTime ? (
          <span>
            {template.defaultStartTime.slice(0, 5)} - {template.defaultEndTime.slice(0, 5)}
          </span>
        ) : (
          <span className="text-muted-foreground">Non défini</span>
        )}
      </TableCell>
      <TableCell className="space-y-1">
        {template.tags.length ? (
          template.tags.map((tag) => (
            <Badge key={tag.id} variant="secondary">
              {tag.label}
            </Badge>
          ))
        ) : (
          <span className="text-muted-foreground">Aucun tag</span>
        )}
      </TableCell>
      <TableCell>
        {template.defaultVenue ? (
          template.defaultVenue.name
        ) : (
          <span className="text-muted-foreground">Aucune</span>
        )}
        {updateTemplate.isError ? (
          <p className="text-xs text-destructive">Une erreur est survenue</p>
        ) : null}
      </TableCell>
    </TableRow>
  );
}

function InlineTemplateEditor({
  templateId,
  onClose,
}: {
  templateId: string;
  onClose: () => void;
}) {
  const { data: templates } = useMissionTemplates();
  const template = templates?.find((item) => item.id === templateId);
  const { data: tags } = useMissionTags();
  const { data: venues } = useVenues();
  const updateTemplate = useUpdateMissionTemplate(templateId);
  const [localState, setLocalState] = useState<MissionTemplateCreate>(() => ({
    name: template?.name ?? "",
    description: template?.description ?? "",
    teamSize: template?.teamSize ?? 1,
    requiredSkills: template?.requiredSkills ?? [],
    defaultStartTime: template?.defaultStartTime ?? "",
    defaultEndTime: template?.defaultEndTime ?? "",
    defaultVenueId: template?.defaultVenueId ?? undefined,
    tagIds: template?.tags.map((tag) => tag.id) ?? [],
  }));

  useEffect(() => {
    if (template) {
      setLocalState({
        name: template.name,
        description: template.description ?? "",
        teamSize: template.teamSize,
        requiredSkills: template.requiredSkills,
        defaultStartTime: template.defaultStartTime ?? "",
        defaultEndTime: template.defaultEndTime ?? "",
        defaultVenueId: template.defaultVenueId ?? undefined,
        tagIds: template.tags.map((tag) => tag.id),
      });
    }
  }, [template]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await updateTemplate.mutateAsync({
        ...localState,
        defaultVenueId: localState.defaultVenueId || undefined,
        defaultStartTime: localState.defaultStartTime || undefined,
        defaultEndTime: localState.defaultEndTime || undefined,
      });
      onClose();
    } catch (error) {
      // L'état d'erreur est géré par React Query.
    }
  };

  if (!template) {
    return null;
  }

  return (
    <form
      data-testid={`mission-template-editor-${templateId}`}
      className="space-y-3 rounded-md border border-border bg-muted/50 p-3"
      onSubmit={handleSubmit}
    >
      <div className="grid gap-3 md:grid-cols-2">
        <div className="space-y-1">
          <Label htmlFor={`edit-name-${templateId}`}>Nom</Label>
          <Input
            id={`edit-name-${templateId}`}
            value={localState.name}
            onChange={(event) => setLocalState((state) => ({ ...state, name: event.target.value }))}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor={`edit-team-size-${templateId}`}>Taille</Label>
          <Input
            id={`edit-team-size-${templateId}`}
            type="number"
            min={1}
            value={localState.teamSize}
            onChange={(event) =>
              setLocalState((state) => ({ ...state, teamSize: Number(event.target.value) }))
            }
          />
        </div>
      </div>
      <div className="space-y-1">
        <Label htmlFor={`edit-description-${templateId}`}>Description</Label>
        <Textarea
          id={`edit-description-${templateId}`}
          value={localState.description ?? ""}
          onChange={(event) =>
            setLocalState((state) => ({ ...state, description: event.target.value }))
          }
        />
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <div className="space-y-1">
          <Label htmlFor={`edit-start-${templateId}`}>Début</Label>
          <Input
            id={`edit-start-${templateId}`}
            type="time"
            value={localState.defaultStartTime ?? ""}
            onChange={(event) =>
              setLocalState((state) => ({ ...state, defaultStartTime: event.target.value }))
            }
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor={`edit-end-${templateId}`}>Fin</Label>
          <Input
            id={`edit-end-${templateId}`}
            type="time"
            value={localState.defaultEndTime ?? ""}
            onChange={(event) =>
              setLocalState((state) => ({ ...state, defaultEndTime: event.target.value }))
            }
          />
        </div>
      </div>
      <div className="space-y-1">
        <Label htmlFor={`edit-venue-${templateId}`}>Salle</Label>
        <select
          id={`edit-venue-${templateId}`}
          className="w-full rounded-md border border-input bg-background p-2 text-sm"
          value={localState.defaultVenueId ?? ""}
          onChange={(event) =>
            setLocalState((state) => ({
              ...state,
              defaultVenueId: event.target.value || undefined,
            }))
          }
        >
          <option value="">Aucune</option>
          {(venues ?? []).map((venue) => (
            <option key={venue.id} value={venue.id}>
              {venue.name}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1">
        <Label htmlFor={`edit-tags-${templateId}`}>Tags</Label>
        <select
          id={`edit-tags-${templateId}`}
          multiple
          className="h-24 w-full rounded-md border border-input bg-background p-2 text-sm"
          value={localState.tagIds}
          onChange={(event) => {
            const options = Array.from(event.target.selectedOptions).map((option) => option.value);
            setLocalState((state) => ({ ...state, tagIds: options }));
          }}
        >
          {(tags ?? []).map((tag) => (
            <option key={tag.id} value={tag.id}>
              {tag.label}
            </option>
          ))}
        </select>
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="ghost" onClick={onClose}>
          Annuler
        </Button>
        <Button type="submit" disabled={updateTemplate.isPending}>
          {updateTemplate.isPending ? "Sauvegarde..." : "Sauvegarder"}
        </Button>
      </div>
      {updateTemplate.isError ? (
        <p role="alert" className="text-sm text-destructive">
          Impossible de sauvegarder le gabarit.
        </p>
      ) : null}
    </form>
  );
}
