import pkg from '@/package.json';

export default function VersionProject(){

    const p = 'text-emerald-400';

    return(
        <p className={p}>
            Versão {pkg.version}
        </p>
    )
}