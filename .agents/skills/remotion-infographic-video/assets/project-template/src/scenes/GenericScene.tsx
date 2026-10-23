import React from 'react';
import { Sequence, staticFile } from 'remotion';
import { ASSET_BY_ID, SHOT_BADGES } from '../data/assets';
import { COMPONENT_MAP } from '../components';
import { isComponentName } from '../components/registry';
import { Shot } from '../components/Shot';
import { ContentArea } from '../layout/ContentArea';
import { useLayout } from '../layout/useLayout';
import { COLORS } from '../theme/tokens';
import { FONT_SANS } from '../theme/fonts';
import { shotRange } from './useLines';
import type { SceneProps, ShotData } from './types';

const FADE = 20;

const firstNumber = (s: string): number | undefined => {
  const m = s.match(/-?\d+(?:\.\d+)?/);
  return m ? Number(m[0]) : undefined;
};

const Caption: React.FC<{ text: string }> = ({ text }) => {
  const L = useLayout();
  return <div style={{ fontFamily: FONT_SANS, fontSize: L.font('h3'), fontWeight: 700, color: COLORS.text, textAlign: 'center' }}>{text}</div>;
};

/** 按 shot.component 从注册表渲染单个镜头；缺省 props 由 shot 数据补齐 */
export const ShotContent: React.FC<{ shot: ShotData; duration: number }> = ({ shot, duration }) => {
  const p = (shot.props ?? {}) as Record<string, unknown>;
  const text = typeof p.text === 'string' ? p.text : shot.description;
  const dn = shot.display_numbers?.[0];
  const source = typeof p.source === 'string' ? p.source : dn ? `来源 ${dn.source_claim_id}` : undefined;
  const badge = SHOT_BADGES.find((b) => b.shot_no === shot.shot_no)?.text;
  const asset = shot.asset_ids?.map((id) => ASSET_BY_ID[id]).find((a) => a && a.usable);
  const name = isComponentName(shot.component) ? shot.component : undefined;
  if (!name) return <Caption text={text} />;
  const C = COMPONENT_MAP[name];
  switch (name) {
    case 'SlamTitle': return <C text={text} at={0} />;
    case 'KeywordPulse': return <C text={text} range={{ from: 0, to: duration }} />;
    case 'StepList': {
      const items = Array.isArray(p.items) ? (p.items as string[]) : [text];
      const step = duration / Math.max(1, items.length);
      return <C items={items} ranges={items.map((_, i) => ({ from: i * step, to: (i + 1) * step }))} />;
    }
    case 'NumberRoll': return <C value={typeof p.value === 'number' ? p.value : firstNumber(dn?.text ?? text) ?? 0} at={0} suffix={typeof p.suffix === 'string' ? p.suffix : ''} source={source} />;
    case 'CompareBars': return <C items={Array.isArray(p.items) ? p.items : (shot.display_numbers ?? []).map((d) => ({ label: d.text, value: firstNumber(d.text) ?? 0 }))} at={0} source={source} illustrative={shot.illustrative} />;
    case 'SourceBadge': return <C text={badge ?? text} />;
    case 'IllustrativeTag': return <C />;
    case 'MediaCard': return asset ? <C src={staticFile(asset.file.replace(/^(project\/)?public\//, ''))} at={0} attribution={badge ?? (asset.attribution || undefined)} /> : <Caption text={text} />;
    case 'FollowCTA': return <C text={text} at={0} />;
    case 'HoldFade': return <C startAt={Math.max(0, duration - FADE)} durationInFrames={FADE}><Caption text={text} /></C>;
    case 'Split': return <C primary={<Caption text={text} />} secondary={source ? <Caption text={source} /> : <Caption text={shot.description} />} />;
    case 'GlassPanel': return <C><Caption text={text} /></C>;
    case 'ImpactShake': return <C at={0}><Caption text={text} /></C>;
    case 'Shot': return <C entrance={shot.entrance} at={0}><ContentArea><Caption text={text} /></ContentArea></C>;
    case 'SectionTransition': return <Caption text={text} />;
    default: return <Caption text={text} />;
  }
};

/** 缺少 src/scenes/<Sxx>.tsx 时的兜底场景：每个镜头按时间依次出现 */
export const GenericScene: React.FC<SceneProps> = ({ section, shots }) => (
  <>
    {shots.map((sh) => {
      const r = shotRange(sh, section);
      return (
        <Sequence key={sh.shot_no} from={r.from} durationInFrames={Math.max(1, r.to - r.from)}>
          <Shot entrance={sh.entrance} at={0}>
            <ContentArea>
              <ShotContent shot={sh} duration={r.to - r.from} />
            </ContentArea>
          </Shot>
        </Sequence>
      );
    })}
  </>
);
export default GenericScene;
