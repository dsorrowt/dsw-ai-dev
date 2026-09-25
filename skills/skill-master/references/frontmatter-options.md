# Optional Frontmatter Fields

A skill needs only `name` and `description`. `disable-model-invocation` is the single field that
changes how a runtime selects a skill; no other optional field belongs in a skill of this framework.

## Fields the runtimes read

| Runtime | Recognized in `SKILL.md` |
|---------|--------------------------|
| omp | `name`, `description`, `globs`, `alwaysApply`, `hide`, `disableModelInvocation` (the kebab-case spelling `disable-model-invocation` is normalized to it) |
| pi (Agent Skills) | `name`, `description`, `disable-model-invocation` |

Every other key is outside both contracts: omp keeps it as unknown metadata and acts on none of it,
and no pi Agent Skills field reads it. The Claude Code contract is therefore not portable and must
not appear in a skill:

- `allowed-tools` — supported by neither runtime; it does not restrict the skill's tool set.
- `user-invocable` — supported by neither runtime; it does not hide a skill from any menu.
- `argument-hint` — supported by neither runtime; it renders no autocomplete hint.

`globs` and `alwaysApply` are recognized by omp, but their behavior is undocumented, so the
framework's skills do not use them.

### `disable-model-invocation`

The only field that turns skill selection off. In omp, `disableModelInvocation: true` (equivalent to
`hide: true`) removes the skill from the skill list the model sees. In pi, the same field removes
the skill from the model's automatic selection. Neither runtime unloads the skill: it stays
reachable explicitly — `skill://<name>` and `/skill:<name>` in omp, `/skill:name` in pi.

Write the kebab-case spelling: it is the spelling pi's Agent Skills contract uses, and omp
normalizes it to `disableModelInvocation`, so one line disables model invocation in both runtimes.

```yaml
---
name: dangerous-operation
disable-model-invocation: true
---
```

Use for: manual-only skills, destructive or expensive operations that need explicit user consent,
and duplicate skills whose function is already covered by another skill.

### model — not supported

Neither runtime reads a `model` field from `SKILL.md`: omp recognizes only `name`, `description`,
`globs`, `alwaysApply`, `hide`, `disableModelInvocation` and keeps other keys as unknown metadata;
pi follows the Agent Skills field list, which has no model field. Never name a model in a skill. When
a step needs a class of model, name the class (`fast` or `good`) in prose — see the `methodology`
skill, "Model classes"; the class is bound to a concrete model in runtime configuration.
